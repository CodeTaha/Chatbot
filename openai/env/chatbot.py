import openai
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
chat_responses = []

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

chat_log = [{'role':'system',
             'content':'You are a sports coach who gives users information about sports.\
              You will take the physical data of the athletes and interpret them to make an exercise and nutrition plan. You will answer sports-related questions,\
               but you will not accept any other irrelevant questions and will only answer the questions I ask you to answer.\
                When you are asked irrelevant questions, you can say, "I am a sports trainer AI software, I cannot answer such questions."\
                 You will also be able to analyze the progress by examining the analysis of physical data taken on different dates and make a nutrition and exercise plan for the user accordingly.\
                  Instead of writing long questions, you will answer them with short answers.\
                   Once the user enters welcome prompts such as hello in all languages or after the first prompt is typed by the user, explain what you can help them with and ask them for their physical data for detailed physical analysis.'}]

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = openai.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=chat_log,
                temperature=0.6,
                stream=True
            )

            ai_response = ''

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            chat_log.append({'role': 'assistant', 'content': ai_response})
            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break

@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):

    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature=0.6
    )

    bot_response = response.choices[0].message.content
    chat_log.append({'role': 'assistant', 'content': bot_response})
    chat_responses.append(bot_response)

    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})
