from utils.llm import generate_llm_response


def generateFeedBack(query:str, numQuestions = 3):
    userprompt = f"""Given the following query from the user, ask some follow up questions to clarify the research direction. Return a maximum of {numQuestions} questions, but feel free to return less if the original query is clear: <query>{query}</query>
A Sample Good Response would be:
<FollowUp> 
Does the ....
How to ....
Make a .... 
Why the ....
....
</FollowUp>
Each question should be on a new line.
"""
    systemPrompt = "You're a helpful AI" # TODO/FIXME: This is a placeholder. Replace with a more appropriate prompt.
    res = generate_llm_response(system_prompt=systemPrompt, user_prompt=userprompt)
    follow_ups = res.split("<FollowUp>")[1].split("</FollowUp>")[0].strip(" \n").split("\n")
    return follow_ups[:numQuestions]