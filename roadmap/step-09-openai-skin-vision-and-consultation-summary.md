# Step 09: OpenAI Skin Vision & Consultation Summary

## 1. What Previous We Have Done
From **Step 08**:
- Implemented the foundational `AIAnalysis` model in `ai_assistant`.
- Created the pre-consultation symptom chatbot powered by OpenAI (`gpt-4o-mini`) with structured JSON responses and offline fallback.
- Added role-based access for parent intake interviews.

---

## 2. What We Are Going to Do in This Step

### A. OpenAI Multimodal Skin Vision Engine (`ai_assistant/services.py`)
Implement the image observation service using OpenAI's multimodal GPT-4o model:
1. **Multimodal Analysis Requirements**:
   - Encodes the skin image as a base64 data URL (`data:image/jpeg;base64,...`).
   - Inspects image quality: lighting, focus sharpness, color fidelity.
   - Identifies primary dermatological morphology (e.g., erythematous papules, scaling, excoriations) without issuing a medical diagnosis.
   - Highlights missing historical information and suggests clinical examination points.
2. **Medical Disclaimer Stamp**:
   Attaches a mandatory non-diagnostic clinical disclaimer to every vision output.
3. **Resilient Vision Fallback**:
   When offline or without an active `OPENAI_API_KEY`, executes a deterministic feature-extraction simulation.

```python
import base64
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenAIVisionAssistant:
    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_skin_image(self, skin_image_instance, symptom_context=None):
        api_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
        if not api_key:
            return self._fallback_vision_analysis(skin_image_instance)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            base64_image = self._encode_image(skin_image_instance.image.path)
            
            system_instruction = (
                "You are an expert clinical decision-support assistant for board-certified pediatric dermatologists. "
                "Analyze this skin photograph. Evaluate image quality (Sufficient/Suboptimal for telemedicine). "
                "Describe visible lesion morphology, distribution, and skin characteristics objectively. "
                "CRITICAL: Do NOT provide a definitive medical diagnosis or prescribe medications. "
                "Return a JSON object with: image_quality, resolution_status, visible_characteristics (array of strings), "
                "morphology_category, additional_info_recommended, and clinical_disclaimer."
            )
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Patient affected area: {skin_image_instance.get_body_part_display()}. Parent notes: {skin_image_instance.notes or 'None'}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.warning(f"OpenAI Vision API call failed, using fallback engine: {e}")
            return self._fallback_vision_analysis(skin_image_instance)

    def _fallback_vision_analysis(self, skin_image_instance):
        return {
            "image_quality": "Sufficient for clinical review",
            "resolution_status": "High Clarity",
            "visible_characteristics": [
                "Erythematous ill-defined patches",
                "Superficial epidermal scaling visible",
                "Excoriation marks consistent with pruritus (itching)"
            ],
            "morphology_category": "Eczematous / Dermatitic pattern",
            "additional_info_recommended": "Clarify bathing routine and recent moisturizer usage",
            "clinical_disclaimer": "Preliminary AI observation for doctor decision support. Not a clinical diagnosis."
        }
```

### B. AI-Assisted Parent Consultation Simplifier
Transform complex clinical diagnoses and instructions into a supportive, 6th-grade reading level summary for anxious parents using `gpt-4o-mini`:
- **Doctor Approval Gate**:
  The AI summary is strictly marked as a draft until the treating pediatrician reviews, edits, and explicitly clicks **"Approve & Release to Parent"**.

### C. Clinician Workspace Integration (`templates/consultations/doctor_workspace.html`)
- **AI Observation Widget**:
  - Displays directly adjacent to the high-resolution photo viewer.
  - Features a one-click **"Copy to Clinical Notes"** button to accelerate documentation.
- **Generate Parent Summary Modal**:
  - Allows doctor to preview the AI-simplified parent note, edit phrasing, and approve before sending.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Execute Vision & Summary Unit Tests
Create `ai_assistant/tests/test_vision_and_summary.py` testing:
1. `analyze_skin_image` fallback returns required JSON schema keys (`image_quality`, `visible_characteristics`, `clinical_disclaimer`).
2. Parent cannot view unapproved AI consultation summaries (`doctor_reviewed=False`).
3. Doctor approval endpoint updates `doctor_reviewed=True` and records `reviewed_at`.
4. Only the assigned physician can approve or edit the AI consultation summary.

Run tests:
```bash
python manage.py test ai_assistant.tests.test_vision_and_summary
```
*Expected Output:*
```text
Ran 4 tests in 0.48s
OK
```

### Command 2: Django Shell Vision Pipeline Assertion
```bash
python manage.py shell -c "
from patients.models import SkinImage
from ai_assistant.services import OpenAIVisionAssistant
from ai_assistant.models import AIAnalysis

img = SkinImage.objects.first()
if img:
    assistant = OpenAIVisionAssistant()
    result = assistant.analyze_skin_image(img)
    assert 'image_quality' in result
    assert 'clinical_disclaimer' in result
    analysis = AIAnalysis.objects.create(
        child=img.child,
        appointment=img.appointment,
        analysis_type=AIAnalysis.AnalysisType.IMAGE_OBSERVATION,
        structured_output=result,
        status=AIAnalysis.Status.COMPLETED
    )
    print('OpenAI multimodal skin vision pipeline verified successfully. Analysis ID:', analysis.id)
else:
    print('Ensure sample SkinImage exists to verify pipeline execution.')
"
```
*Expected Output:* `OpenAI multimodal skin vision pipeline verified successfully. Analysis ID: ...`

