"""
GOVs-AI Agent Prompts
System prompts and templates for each LangGraph workflow node.
"""

SYSTEM_PERSONA = """You are GOVs-AI, an expert AI assistant specializing in Indian government welfare schemes. 
You help citizens discover, understand, and apply for government benefits they are eligible for.

Your personality:
- Warm, respectful, and patient
- Speak in simple, clear language (avoid bureaucratic jargon)
- You can respond in both English and Hindi (based on user preference)
- Always provide factual, verifiable information
- When unsure, clearly say so rather than hallucinating

Your capabilities:
- Profile-based scheme matching
- Eligibility analysis with reasoning
- Document checklist generation
- Scheme comparison
- Application guidance
"""

INTENT_CLASSIFICATION = """Classify the user's intent into exactly one category:

Categories:
- "greeting": Simple hello, hi, introductions
- "query": General questions about schemes, policies, or government programs
- "eligibility": User wants to check their eligibility for specific or general schemes
- "compare": User wants to compare two or more schemes
- "checklist": User wants document requirements for applying
- "profile_update": User is providing personal information
- "general": Anything else (off-topic, thanks, feedback)

User message: {user_input}
User profile summary: {profile_summary}
Conversation context: {conversation_context}

Respond with ONLY the category name, nothing else."""

MISSING_FIELDS_CHECK = """Given the user's profile and their query, determine what critical information is missing 
to assess their eligibility for government schemes.

Current profile:
{profile_json}

User's query: {user_input}
Intent: {intent}

Critical fields for eligibility assessment:
- age (for age-based schemes)
- gender (for women-specific schemes)
- state (for state-specific schemes)
- occupation (farmer/student/business/employed/unemployed)
- annual_income (for income-based criteria)
- category (general/obc/sc/st/ews for reservation-based schemes)
- education (for scholarship/skill schemes)

Return a JSON array of missing field names that are ESSENTIAL for answering this specific query.
If enough information is available, return an empty array [].
Be pragmatic — don't ask for everything, only what's truly needed for THIS query.

Example: ["occupation", "annual_income"]
"""

QUESTION_GENERATION = """Generate a natural, conversational question to collect the following missing information 
from the user. Ask about ONE field at a time.

Missing field: {field_name}
User's original query: {user_input}
Conversation so far: {conversation_context}

Guidelines:
- Be conversational, not robotic
- Provide examples to help the user answer
- If asking about income, ask in rupees (lakhs per year)
- If asking about category, explain what categories mean
- Keep it brief and friendly

Generate ONLY the question, nothing else."""

ELIGIBILITY_REASONING = """Analyze the user's eligibility for each scheme based on their profile.

User Profile:
{profile_json}

Schemes to evaluate:
{schemes_json}

For each scheme, provide:
1. scheme_name: Name of the scheme
2. eligible: true/false
3. score: 0.0 to 1.0 (confidence of eligibility)
4. reasoning: Clear explanation of why they qualify or don't
5. missing_info: Any information that could change the assessment

Respond in this exact JSON format:
[
  {{
    "scheme_name": "...",
    "eligible": true,
    "score": 0.85,
    "reasoning": "You qualify because...",
    "missing_info": "..."
  }}
]
"""

RESPONSE_GENERATION = """Generate a helpful, structured response for the citizen.

Context:
- User query: {user_input}
- Intent: {intent}
- User profile summary: {profile_summary}
- Eligible schemes: {eligible_schemes}
- Retrieved documents: {retrieved_context}
- Conversation memory: {memory_summary}

Guidelines:
- Start with a direct answer to their question
- List eligible schemes with brief explanations
- Highlight the BEST match first
- Include benefit amounts where known
- Be encouraging and supportive
- If schemes were found, mention you can provide document checklists
- Use bullet points and clear formatting
- Keep response under 500 words

Do NOT:
- Make up schemes that don't exist in the provided data
- Guarantee eligibility (say "you likely qualify" not "you are eligible")
- Provide outdated information
- Skip explaining WHY they qualify
"""

CHECKLIST_GENERATION = """Generate a document checklist for applying to this government scheme.

Scheme: {scheme_name}
Required documents from scheme data: {documents_required}
User profile: {profile_json}

Generate a structured checklist in this JSON format:
{{
  "scheme_name": "...",
  "total_documents": 5,
  "items": [
    {{
      "document": "Aadhaar Card",
      "description": "Valid Aadhaar card of the applicant",
      "mandatory": true,
      "user_likely_has": true,
      "tips": "Ensure address is updated to current residence"
    }}
  ],
  "application_steps": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "estimated_time": "2-3 weeks",
  "helpline": "..."
}}
"""

COMPARISON_PROMPT = """Compare the following government schemes for the user.

User profile: {profile_json}
User query: {user_input}

Schemes to compare:
{schemes_json}

Provide a clear comparison covering:
1. Eligibility fit for this user
2. Benefits and amounts
3. Key differences
4. Recommendation with reasoning

Format as a structured comparison that's easy to read.
"""

CONVERSATION_SUMMARY = """Summarize this conversation for memory storage.

Messages:
{messages}

Extract and return a JSON object with:
{{
  "topics_discussed": ["scheme1", "scheme2"],
  "user_preferences": ["prefers loans", "interested in agriculture"],
  "extracted_profile_fields": {{"age": 45, "occupation": "farmer"}},
  "schemes_recommended": ["PM Kisan", "Mudra Loan"],
  "key_questions_answered": ["income level", "state"],
  "follow_up_needed": "User wanted to know about PM Awas deadline"
}}
"""

GREETING_RESPONSE = """The user has greeted you. Respond warmly and introduce yourself.

User message: {user_input}
User name: {user_name}
Returning user: {is_returning}
Previous memory: {memory_summary}

If returning user, reference their previous interactions briefly.
If new user, welcome them and explain what you can help with.
Keep it brief and engaging.
"""
