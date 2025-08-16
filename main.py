from openai import OpenAI
import whisper
import time


def main_(audio_file):
    # the main function will lead the entire program, it will contain the all the major code needed to run the program
    # and I will call the other programs inside this main_ function
    # audio_file = "test_medicalAudio.mp3"
    
    whisper_model = whisper.load_model("small")
    result_text = whisper_model.transcribe(audio_file)
    
    # Initialize OpenAI client
    client = OpenAI(api_key="sk-proj-fgiK2JJBytLimDDWj-TgKTenrTWq5lVc6wkkfoAtKcuAV2j52HEzFK" +
                    "JImKl09XS6c6Jtl8KxjQT3BlbkFJA46oPAdG3DCxwG-DXITmthCNciQXwI73o1-HiaAuqu0BTrWnZFXAuJHyRzMIZ3zL4SA5f1X1EA")
    
    # get inputs from files
    raw_transcript_file = "test_transcript.txt"
    raw_medicalNote_file = "test_medicalNote.txt"
    
    # holds the transcribed dialogue
    transcribed_text = transcribe_ai(result_text["text"], client)
    medical_note_text = None
    try: # this checks if the file is present and 
        with open(raw_transcript_file, 'r') as file:
            transcript_file = file.read()
        with open(raw_medicalNote_file, 'r') as file:
            medicalNote_file = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{transcript_file}' was not found.")
        transcript_file = None
        # medicalNote_file = None
    
    if transcript_file is not None:
        medical_note_text = medical_note_json(transcribed_text, medicalNote_file, transcript_file, client)
    
    official_medicalNotes = medical_note_generator(medical_note_text, client)
    
    print("++++++++++++++++++++++++TRANSCRIBED_DIALOGUE+++++++++++++++++++++++++")
    print(transcribed_text)
    print()
    print("++++++++++++++++++++++++CLINICAL_NOTE_JSON+++++++++++++++++++++++++++")
    print(medical_note_text)
    print()
    print("++++++++++++++++++CLINICAL_NOTES+++++++++++++++++++++")
    print(official_medicalNotes)
    
    return official_medicalNotes
    
def transcribe_ai(transcript_text, ai_things):
    #returns the dialogue transcript
    
    
    
    prompt = f""" 
    You are given a block of conversation text from a medical setting between a doctor and a patient(s) or other personel. 
    Your task is to:
    1. Estimate the number of unique speakers.
    2. Identify each speaker with appropriate labels (e.g., Doctor, Patient, Nurse, etc.).
    3. Structure the dialogue clearly with speaker labels before each line.
    4. Preserve all details relevant to the medical context such as symptoms, medications, dates, and any clarifications by the doctor or patient.

    Transcript:
    {transcript_text}
    """ 

    # Send request to GPT model
    response = ai_things.chat.completions.create(
        model="gpt-4o-mini",  # available models gpt-4o, gpt-4o-mini, or gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are an expert dialogue analyzer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


def medical_note_json(dialogue_text, medical_note_example, transcript_example, ai_things):
    # return a medical note 
    
    prompt = """
    You are a clinical conversation → clinical-note parser **and** coverage auditor.  
    Return **valid JSON only** that matches the schema below.  
    Do **not** invent facts; if something is missing from the input, leave that field `""` or `[]`, and mark it as **not discussed** in the audit.  
    Cite short evidence snippets (≤120 chars) from the input for every item you claim is present.  
    Prefer the transcript over assumptions. Ignore disfluencies and greetings.

    **JSON schema (must match exactly):**
    {
    "note": {
        "subjective": {
        "hpi": "",
        "ros": "",
        "pmh": "",
        "psh": "",
        "medications": [],
        "personal_note": "",
        "allergies": "",
        "social_history": "",
        "family_history": ""
        },
        "objective": {
        "vitals": {
            "temperature": "",
            "blood_pressure": "",
            "heart_rate": "",
            "respiratory_rate": "",
            "oxygen_saturation": ""
        },
      "physical_exam": "",
      "labs_imaging": ""
    },
    "assessment": "",
    "plan": {
      "diagnostics": [],
      "med_changes": [],
      "nonpharm": [],
      "referrals": [],
      "follow_up": "",
      "safety_net": ""
    },
    "mdm": ""
  },
  "coverage_audit": [
    {
      "item": "Allergies",
      "present": true,
      "evidence": ["..."],
      "confidence": "high|medium|low"
    }
  ],
  "not_discussed": [],
  "inconsistencies": [],
  "assertions_without_evidence": []
    }

    **Coverage checklist (audit against all of these):**
    - Demographics (name/age/sex if present in text)
    - Allergies
    - Medications (name/dose/route/frequency if present)
    - PMH, PSH, Family history, Social history
    - HPI (onset, location, duration, character, aggravating/relieving, severity, timing) — flag missing sub-elements
    - ROS (positives+negatives)
    - Vitals (T, BP, HR, RR, SpO₂)
    - Physical exam
    - Labs/Imaging (if any)
    - Assessment (working dx +/- differentials)
    - Plan: diagnostics, med changes, non-pharm advice, referrals, follow-up, safety-netting
    - MDM (complexity/risks/rationale)

    Rules:
    - Populate `coverage_audit` with one entry per checklist item (even if absent).  
    - When absent, set `present:false`, include `evidence:[]`, and list the item in `not_discussed`.  
    - If you produce any statement in the note without a direct quote or clear paraphrase in the input, add a short description to `assertions_without_evidence`.  
    - If the transcript contradicts itself (e.g., “no allergies” and later “penicillin rash”), add a short entry to `inconsistencies` with two evidence snippets.

    You will be given:
    1) Optional **few-shot examples** showing the desired style and JSON.
    2) The **source text** (transcription or free-text note).

    Return **JSON only**, conforming to the schema.
    """ + f"""
    **Examples:**
    {medical_note_example}

    **Source text Example:**
    {transcript_example}
    
    **Important**
    This is the dialogue text you should work 
    {dialogue_text}
    """
    
    # Send request to GPT model
    response = ai_things.chat.completions.create(
        model="gpt-4o-mini",  # available models gpt-4o, gpt-4o-mini, or gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are an expert clinical-note parser and coverage auditor"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    return response.choices[0].message.content


def medical_note_generator(json_file, ai_things):
    # this will return the medical note in the correct format
    
    prompt = f"""
    You are a medical documentation assistant. Your job is to take structured patient information in JSON format and generate a clear, concise, and professional **clinical note** for the medical record.  

### Instructions:
- Only use information provided in the JSON; do not invent or guess details.  
- Organize the note into the following sections (leave blank if not available in the JSON):  
- Do not include "*" in the output
  - Patient Name  
  - Date of Birth  
  - Age  
  - Sex  
  - Medical Record #  
  - Date of clinic visit  
  - Primary care provider  
  - Personal note (optional, if relevant)  
  - History of Present Illness (HPI)  
  - Allergies  
  - Medications  
  - Previous History (Past Medical History, Past Surgical History, Family History, Social History)  
  - Review of Systems  
  - Physical Exam  
  - Vital Signs  
  - Assessment  
  - Plan  
  - Medical Decision Making  

    - Write the note in professional medical language, complete sentences, and third-person narration.  
    - Use standard clinical note style, not bullet points, unless the information is inherently a list (e.g., medications).  
    - Include ICD-10 codes if explicitly provided in the JSON.  
    - If data is missing in the JSON, leave that section empty rather than inventing information.  
    - If you see any information in the json that will be very valuable to the doctor make sure you include it as well
    ### Input JSON:
    {json_file}

    ### Output:
    Clinical Note: 
    """
    
    # Send request to GPT model
    response = ai_things.chat.completions.create(
        model="gpt-4o-mini",  # available models gpt-4o, gpt-4o-mini, or gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are an expert clinical-note parser and coverage auditor"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# def generate_medical_note():
#     return "[MEDICAL NOTE INSERT]"
    

if __name__ == "__main__":
    OB_BO = None
    start_time = time.perf_counter()
    main_("test_medicalAudio.mp3") 
    end_time = time.perf_counter()
    run_time = end_time - start_time
    # print(generate_medical_note())
    print(f"The code took {run_time:.4f} seconds to run.")
    
