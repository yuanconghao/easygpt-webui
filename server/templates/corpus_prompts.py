ROLE_STYLE_DETAIL = {
    "warm": "reflect your empathy and understanding, make students feel comfortable and accepted, provide a supportive learning environment, and enhance their academic growth",
    "enthusiastic": "reflect your passion for the subject matter, ignite students' interest in learning, provide an energetic classroom atmosphere, and stimulate their academic curiosity",
    "strict": "reflect your high standards and expectations, encourage students' discipline and focus, provide a structured learning environment, and foster their academic rigor and responsibility",
    "heuristic": "reflect your belief in self-learning, encourage students' exploration and discovery, provide a stimulating learning environment, and foster their critical thinking and problem-solving skills",
    "encouraging": "reflect your positive attitude towards learning, boost students' confidence in their abilities, provide continuous support and motivation, and foster their academic growth and development",
    "directive": "reflect your clear and precise instructions, guide students' learning process, provide a well-defined path for their academic journey, and foster their understanding and mastery of the subject",
    "interactive": "reflect your emphasis on communication, encourage students' active participation in class, provide a dynamic and engaging learning environment, and foster their collaborative and interpersonal skills",
    "discussion": "reflect your value for diverse perspectives, encourage students' active participation and critical thinking, provide a platform for open dialogue and debate, and foster their communication skills and understanding of the topic",
    "practical": "reflect your focus on real-world applications, encourage students' understanding of the relevance of their studies, provide hands-on learning experiences, and foster their problem-solving skills and readiness for the professional world",
}

CEFR_LEVEL_ROUNDS = {
    "pre-A1": 3,
    "A1": 3,
    "A2": 4,
    "B1": 5,
}

CEFR_LEVEL_WORDS = {
    "pre-A1": 12,
    "A1": 16,
    "A2": 20,
    "B1": 25,
}

CORPUS_BASIC_TEMPLATE = "You will play my English teacher {role_name}, Your teaching style is {role_style}, which can {role_style_detail}.The English level of the student is at CEFR {cefr_level}. Please generate {cefr_level_rounds} talking rounds that the words counts within {cefr_level_words} in each sentence."
CORPUS_WORDS_TEMPLATE = "The dialogue should include the words '{words}'"
CORPUS_SENTENCE_TEMPLATE = "The dialogue should include these sentences '{sentence}'"
CORPUS_GOAL_TEMPLATE = ""
CORPUS_BACKGROUND_TEMPLATE = ""
CORPUS_CHARACTERS_TEMPLATE = ""
CORPUS_EXAMPLE_TEMPLATE = ""
CORPUS_FORMAT_TEMPLATE = ". Provide output in JSON format as follows:[{\"role\":\"assistant\",\"content\":\"\"},{\"role\":\"user\",\"content\":\"\"}], Directly output JSON data."



# CORPUS_TEMPLATE = f"""Given MY INTENDED AUDIENCES and HOPING TO SOLVE using a language model, please select \
# the model prompt that best suits the input.
# You will be provided with the prompt, variables, and an opening statement.
# Only the content enclosed in double curly braces, such as {{variable}}, in the prompt can be considered as a variable; \
# otherwise, it cannot exist as a variable in the variables.
# If you believe revising the original input will result in a better response from the language model, you may \
# suggest revisions.
#
# << FORMATTING >>
# Return a markdown code snippet with a JSON object formatted to look like, \
# no any other string out of markdown code snippet:
# ```json
# {{{{
#     "prompt": string \\ generated prompt
#     "variables": list of string \\ variables
#     "opening_statement": string \\ an opening statement to guide users on how to ask questions with generated prompt \
# and fill in variables, with a welcome sentence, and keep TLDR.
# }}}}
# ```
#
# << EXAMPLES >>
# [EXAMPLE A]
# ```json
# {
#   "prompt": "Write a letter about love",
#   "variables": [],
#   "opening_statement": "Hi! I'm your love letter writer AI."
# }
# ```
# """
