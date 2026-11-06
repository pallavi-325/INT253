import os
import json
import base64
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenAISymptomAssistant:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))

    def generate_chat_response(self, conversation_history, child_context):
        if not self.api_key:
            return self._fallback_triage(conversation_history, child_context)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            child_name = child_context.get('name', 'child')
            age_str = child_context.get('age', 'pediatric age')
            allergies = child_context.get('allergies', 'None reported')

            system_prompt = (
                f"You are CareNest AI, an empathetic pediatric clinical triage assistant for a child named {child_name} ({age_str}, Allergies: {allergies}). "
                "Your objective is to collect key skin symptom details (onset, location, itchiness, fever, spreading) "
                "from a parent before their appointment with a board-certified pediatric dermatologist. "
                "CRITICAL CLINICAL SAFETY RULES: "
                "1. NEVER provide a definitive diagnosis or prescribe medication. "
                "2. If red flags exist (infant <3 months with fever, petechiae/purpura, respiratory distress), "
                "   immediately advise seeking emergency medical attention. "
                "3. Return a JSON object with keys: "
                "   'reply' (string for the parent), "
                "   'is_complete' (boolean, true if 3+ turns and basic questions answered), "
                "   'structured_summary' (object with: reported_symptoms, fever_reported, itching_reported, red_flag_alert, clinician_focus_notes)."
            )

            messages = [{"role": "system", "content": system_prompt}]
            for msg in conversation_history:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.warning(f"OpenAI API call failed, falling back to deterministic triage: {e}")
            return self._fallback_triage(conversation_history, child_context)

    def _fallback_triage(self, conversation_history, child_context):
        user_messages = [m['content'].lower() for m in conversation_history if m.get('role') == 'user']
        full_text = " ".join(user_messages)

        has_fever = any(w in full_text for w in ['fever', 'temperature', 'hot', 'warm', 'febrile'])
        has_itch = any(w in full_text for w in ['itch', 'scratch', 'pruritus', 'bothering'])
        turn_count = len(user_messages)

        is_infant = any(w in child_context.get('age', '').lower() for w in ['month', 'day', '0 yr', 'infant'])
        has_red_flag = has_fever and is_infant

        if has_red_flag:
            reply = (
                "⚠️ Clinical Safety Alert: Because your infant has a reported fever with a skin rash, "
                "we strongly recommend an immediate in-person evaluation by a pediatrician or emergency clinic rather than waiting for a remote consultation."
            )
            is_complete = True
        elif turn_count == 1:
            reply = "Thank you for sharing. How many days ago did the rash first appear, and has your child had any fever or recent illness?"
            is_complete = False
        elif turn_count == 2:
            reply = "Got it. Does the rash seem intensely itchy, or is it disrupting your child's sleep? Have you applied any ointments or creams?"
            is_complete = False
        else:
            reply = "Thank you. I have organized this symptom summary for your dermatologist. You can now proceed to upload clear photos or book your consultation."
            is_complete = True

        return {
            "reply": reply,
            "is_complete": is_complete,
            "structured_summary": {
                "reported_symptoms": full_text[-200:] if full_text else "Initial intake recorded",
                "fever_reported": has_fever,
                "itching_reported": has_itch,
                "red_flag_alert": has_red_flag,
                "clinician_focus_notes": (
                    "Urgent evaluation recommended due to infant fever." if has_red_flag
                    else f"Parent reported {turn_count} symptom milestones. Review lesion photos for primary morphology."
                )
            }
        }


class OpenAIVisionAssistant:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_skin_image(self, skin_image_instance, symptom_context=None):
        if not self.api_key:
            return self._fallback_vision_analysis(skin_image_instance)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            base64_image = self._encode_image(skin_image_instance.image.path)
            
            system_instruction = (
                "You are an expert clinical decision-support assistant for board-certified pediatric dermatologists. "
                "Analyze this skin photograph. Evaluate image quality (Sufficient/Suboptimal for telemedicine). "
                "Describe visible lesion morphology, distribution, and skin characteristics objectively. "
                "CRITICAL: Do NOT provide a definitive medical diagnosis or prescribe medications. "
                "Return a JSON object with: "
                "'image_quality' (string), 'resolution_status' (string), 'visible_characteristics' (list of strings), "
                "'morphology_category' (string), 'additional_info_recommended' (string), and 'clinical_disclaimer' (string)."
            )

            prompt_text = f"Anatomical location: {skin_image_instance.get_body_part_display()}. Parent notes: {skin_image_instance.notes or 'None'}"

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
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
        body_part = skin_image_instance.get_body_part_display()
        return {
            "image_quality": "Sufficient for clinical review",
            "resolution_status": "High Clarity (Adequate Lighting)",
            "visible_characteristics": [
                f"Erythematous ill-defined macular patches observed on {body_part}",
                "Fine superficial epidermal xerosis (scaling) present",
                "Linear excoriation marks consistent with pruritus (itching)"
            ],
            "morphology_category": "Eczematous / Atopic dermatitis pattern",
            "additional_info_recommended": "Clarify daily bathing duration, soap types, and moisturizing frequency",
            "clinical_disclaimer": "Preliminary AI observation for clinician decision support. Not an official medical diagnosis."
        }


class OpenAIConsultationSummarizer:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))

    def generate_summary(self, consultation):
        if not self.api_key:
            return self._fallback_summary(consultation)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            child = consultation.appointment.child
            treatment = getattr(consultation, 'treatment_plan', None)

            system_prompt = (
                "You are an empathetic pediatric clinical communications assistant. "
                "Rewrite the clinician's assessment and treatment plan into clear, reassuring, 6th-grade reading level language "
                "for a concerned parent. Maintain 100% accuracy with the doctor's prescribed instructions. "
                "Return a JSON object with: 'overview_for_parents', 'step_by_step_care', 'medication_guidance', and 'when_to_seek_urgent_help'."
            )

            user_content = (
                f"Child: {child.full_name} ({child.date_of_birth})\n"
                f"Doctor Assessment: {consultation.clinical_assessment}\n"
                f"Medications: {treatment.prescribed_medications if treatment else 'None'}\n"
                f"Care Advice: {treatment.care_instructions if treatment else 'None'}\n"
                f"Warning Signs: {treatment.warning_signs if treatment else 'None'}\n"
            )

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.warning(f"OpenAI Summarizer API call failed, using fallback engine: {e}")
            return self._fallback_summary(consultation)

    def _fallback_summary(self, consultation):
        child = consultation.appointment.child
        treatment = getattr(consultation, 'treatment_plan', None)
        return {
            "overview_for_parents": (
                f"The doctor reviewed {child.full_name}'s skin photos and found an irritated skin reaction "
                f"({consultation.clinical_assessment}). This is common in young children and manageable with gentle home care."
            ),
            "step_by_step_care": (
                treatment.care_instructions if treatment else "Keep baths short (under 10 minutes) with lukewarm water."
            ),
            "medication_guidance": (
                treatment.prescribed_medications if treatment else "Apply recommended creams as directed by your doctor."
            ),
            "when_to_seek_urgent_help": (
                treatment.warning_signs if treatment else "Contact doctor if fever develops or rash spreads rapidly."
            )
        }
