import asyncio
from openai import AsyncOpenAI
from openai.types.chat import chat_completion

client = AsyncOpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="",
)


async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hello How are you",
            }
        ],
        model="gpt-3.5-turbo",
    )


asyncio.run(main())
print(chat_completion)