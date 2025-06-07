import openai

response = openai.images.generate(
    prompt="Aligator",
    n=1,
    size="1024x1024"
)

print(response.data[0].url)