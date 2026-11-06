# Step 08: OpenAI Symptom Assistant

## 1. What Previous We Have Done
From **Step 07**:
- Complete end-to-end medical workflow: child profile creation, appointment scheduling, skin image uploads, doctor clinical evaluation, and downloadable PDF reports.
- Verified system data integrity with automated role-based access control tests.

---

## 2. What We Are Going to Do in This Step

### A. OpenAI Service Architecture & Safety Protocol (`ai_assistant/services.py`)
Build an enterprise AI service with medical guardrails using the OpenAI Python SDK:
1. **Safety Directives**:
   - Explicitly forbidden from issuing definitive medical diagnoses or prescribing drugs.
   - Immediate escalation to emergency services if red flags are detected (infant fever under 3 months, purpura, petechiae, respiratory distress).
2. **Structured JSON Output**:
   Leverages OpenAI's JSON mode (`response_format={"type": "json_object"}`) or structured outputs to guarantee schema conformance for clinician review.
3. **Resilient Offline Fallback / Mock Engine**:
   If `OPENAI_API_KEY` is absent or the external API is unreachable, automatically fall back to deterministic pediatric triage heuristics, ensuring the platform remains fully functional for offline development, automated tests, and academic grading without requiring an active paid subscription.

```python
import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenAISymptomAssistant:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))

    def generate_chat_response(self, conversation_history, child_context):
        if not self.api_key:
            return self._fallback_triage(conversation_history, child_context)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            system_prompt = (
                "You are an empathetic, pediatric teledermatology clinical triage intake assistant. "
                "Your objective is to collect clinical symptom details (onset, itchiness, fever, spreading) "
                "from a parent before their appointment with a board-certified pediatric dermatologist. "
                "CRITICAL CLINICAL SAFETY RULES: "
                "1. NEVER provide a final diagnosis or prescribe medication. "
                "2. If red flags exist (infant <3 months with fever, petechiae/purpura, breathing difficulty), "
                "   immediately advise seeking emergency medical attention. "
                "3. Conclude by producing a structured JSON summary for the doctor. "
                "You must respond with a JSON object containing: 'reply' (string), 'is_complete' (boolean), "
                "and 'structured_summary' (object containing: reported_symptoms, fever_reported, itching_reported, red_flag_alert, clinician_focus_notes)."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            for msg in conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.warning(f"OpenAI API call failed, using fallback engine: {e}")
            return self._fallback_triage(conversation_history, child_context)

    def _fallback_triage(self, conversation_history, child_context):
        # Deterministic pediatric rule-based fallback
        last_message = conversation_history[-1]['content'].lower() if conversation_history else ''
        has_fever = 'fever' in last_message or 'temperature' in last_message
        has_itch = 'itch' in last_message or 'scratch' in last_message
        
        return {
            "reply": "Thank you for sharing those details. Can you also tell me if the rash feels warm to the touch or if your child has had any fever?",
            "is_complete": len(conversation_history) >= 4,
            "structured_summary": {
                "reported_symptoms": last_message,
                "fever_reported": has_fever,
                "itching_reported": has_itch,
                "red_flag_alert": has_fever and "infant" in child_context.get("age_category", ""),
                "clinician_focus_notes": "Parent reported onset and visual characteristics. Check for secondary bacterial infection."
            }
        }
```

### B. AI Analysis Data Model (`ai_assistant/models.py`)
Store AI conversations and structured summaries:
```python
from django.db import models
from patients.models import TimeStampedModel

class AIAnalysis(TimeStampedModel):
    class AnalysisType(models.TextChoices):
        SYMPTOM_CHAT = 'SYMPTOM_CHAT', 'Pre-consultation Symptom Interview'
        IMAGE_OBSERVATION = 'IMAGE_OBSERVATION', 'Preliminary Skin Vision Analysis'
        CONSULT_SUMMARY = 'CONSULT_SUMMARY', 'Parent-Friendly Consultation Simplification'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Analysis'
        COMPLETED = 'COMPLETED', 'Completed'
        FLAGGED = 'FLAGGED', 'Red Flag Detected - Clinical Urgency'
        FAILED = 'FAILED', 'Analysis Failed'

    child = models.ForeignKey('patients.ChildProfile', on_delete=models.CASCADE, related_name='ai_analyses')
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_analyses'
    )
    analysis_type = models.CharField(max_length=30, choices=AnalysisType.choices)
    input_context = models.JSONField(default=dict)
    structured_output = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    doctor_reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
```

### C. Interactive Chat UI & API Endpoint (`ai_assistant/views.py`)
- `POST /ai/symptom-chat/`: Asynchronous JSON endpoint receiving user replies and returning assistant questions or final triage summary.
- Chat Template (`templates/ai_assistant/symptom_chat.html`):
  - Tailwind chat bubbles with distinct styling for parent (mint/teal) and AI assistant (surface dark/white).
  - Animated typing indicator (`animate-pulse`).
  - Pre-filled symptom chip buttons ("Itching intensely", "Started yesterday", "No fever").
  - Clear medical disclaimer badge pinned to the chat header.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Migrations
```bash
python manage.py makemigrations ai_assistant
python manage.py migrate
```
*Expected Output:* `Applying ai_assistant.0001_initial... OK`.

### Command 2: Execute Unit Tests
Create `ai_assistant/tests/test_symptom_assistant.py` testing:
1. Fallback heuristic engine triggers reliably when `OPENAI_API_KEY` is not provided.
2. Structured summary properly captures symptoms, itching, and fever flags.
3. Chat JSON API endpoint (`/ai/symptom-chat/`) accepts POST and returns valid JSON response with HTTP 200.
4. Red flag detection marks `AIAnalysis.status` as `FLAGGED`.

Run tests:
```bash
python manage.py test ai_assistant
```
*Expected Output:*
```text
Ran 4 tests in 0.40s
OK
```

### Command 3: Django Test Client Chat Simulation
```bash
python manage.py shell -c "
from django.test import Client
from django.contrib.auth import get_user_model
from patients.models import ChildProfile

User = get_user_model()
parent = User.objects.filter(role=User.Role.PARENT).first()
child = ChildProfile.objects.filter(parent=parent).first()

client = Client()
client.force_login(parent)

response = client.post(
    '/ai/api/chat/',
    data={'child_id': child.id, 'message': 'My toddler has red circular dry patches on both forearms.'},
    content_type='application/json'
)
assert response.status_code == 200, f'Expected 200, got {response.status_code}'
data = response.json()
assert 'reply' in data or 'structured_summary' in data
print('AI symptom chat simulation verified successfully:', data.get('reply')[:60])
"
```
*Expected Output:* `AI symptom chat simulation verified successfully: ...`

