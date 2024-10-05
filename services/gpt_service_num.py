import config
from openai import AsyncAssistantEventHandler, AsyncOpenAI

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

class EventHandler(AsyncAssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.response_text = None

    async def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    async def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    async def on_message_done(self, message) -> None:
        print("Message done called with message:", message)

        if hasattr(message, 'content'):
            message_content = message.content[0].text

            if message_content:
                print("Received message content:", message_content)
                annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
                citations = []
                for index, annotation in enumerate(annotations):
                    message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
                    if file_citation := getattr(annotation, "file_citation", None):
                        cited_file = await client.files.retrieve(file_citation.file_id)
                        citations.append(f"[{index}] {cited_file.filename}")

                self.response_text = f"{message_content.value}\n\n" + "\n".join(citations)
            else:
                print("Message content is empty")
        else:
            print("Message has no content attribute")

async def setup_assistant_and_vector_store():
    assistant = await client.beta.assistants.create(
        name="Matrix of numerology",
        instructions="You're an expert on the numerology. Use your knowledge base to answer questions based on the provided book.",
        model="gpt-4o-2024-08-06",
        tools=[{"type": "file_search"}],
    )

    vector_store = await client.beta.vector_stores.create(name="Matrix of numerology")

    file_paths = ["/app/numerology.pdf"]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = await client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    assistant = await client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    return assistant

async def generate_gpt_response_numerology(user_name, energies, assistant):
    handler = EventHandler()
    A0 = energies.get('A0')
    B1 = energies.get('B1')
    C2 = energies.get('C2')
    D3 = energies.get('D3')
    E4 = energies.get('E4')
    F5 = energies.get('F5')
    G6 = energies.get('G6')
    H7 = energies.get('H7')
    Y8 = energies.get('Y8')
    M9 = energies.get('M9')
    N10 = energies.get('N10')
    Q11 = energies.get('Q11')
    T12 = energies.get('T12')
    P13 = energies.get('P13')
    O14 = energies.get('O14')
    L15 = energies.get('L15')
    I16 = energies.get('I16')
    X17 = energies.get('X17')
    V18 = energies.get('V18')
    Z19 = energies.get('Z19')
    R20 = energies.get('R20')
    K21 = energies.get('K21')
    prompt = (
        f"Чат, тебе необходимо составить личный расклад по нумерологии для пользователя {user_name} на основе загруженного файла.\n\n"
        f"1) Объем каждого пункта должен быть около 5-6 предложений.\n"
        f"2) Ты должен выдавать только интерпретации, но не включай ссылки на документы или индексы (например, "
        f"\"[18] matrix.pdf\".\n\n"
        f"3) В тексте ничего не выделяй жирным и курсивом."
        f"4) Нигде в ответе не используй # и *.\n\n"       

        f"Порядок трактования расклада:\n\n"
 
        f"1) Личность и психика\n"
        f"Душа человека (Дом 0 - энергия {A0})\n"
        f"Личность: характер, сильные и слабые стороны (Дом 1 - энергия {B1})\n"
        f"Психика: глубинные установки, страхи, подсознательные программы (Дом 2 - энергия {C2}). Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"2) Чувства и самореализация\n"
        f"Чувства: эмоциональные реакции, воспитание, родительские программы (Дом 3 - энергия {D3})\n"
        f"Самореализация: таланты, способности, волевые качества, цели и достижения (Дом 4 - энергия {E4}). Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"3) Образование и духовное развитие\n"
        f"Образование: уровень интеллекта и духовного развития (Дом 5 - энергия {F5})\n"
        f"Личная активность: действия и мотивация (Дом 7 - энергия {H7}). Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"4) Отношения и ответственность\n"
        f"Потенциал на отношения (Дом 6 - энергия {G6})\n"
        f"Личная ответственность: обязательства и осознание (Дом 8 - энергия {Y8}). Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"5) Опыт и финансовая сфера\n"
        f"Знания и опыт (Дом 9 - энергия {M9})\n"
        f"Финансы: управление материальными ресурсами (Дом 10 - энергия {N10}). Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"6) Личная сила и трансформация\n"
        f"Личная сила (Дом 11 - энергия {Q11})\n"
        f"Личная трансформация (Дом 13 - энергия {P13}).Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"7) Психология и внутренний баланс\n"
        f"Психология: понимание себя и окружающих (Дом 12 - энергия {T12})\n"
        f"Сохранение внутреннего баланса (Дом 14 - энергия {O14}). Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"8) Социальная и семейная сфера\n"
        f"Выражение сексуальности (Дом 15 - энергия {L15})\n"
        f"Умение созидать (Дом 16 - энергия {I16})\n"
        f"Демонстрация талантов (Дом 17 - энергия {X17})\n"
        f"Обустройство быта (Дом 18 - энергия {V18})\n"
        f"Умение управлять (Дом 19 - энергия {Z19})\n"
        f"Поддержание родовых связей (Дом 20 - энергия {R20}).\n"
        f"Расширение контактов (Дом 21 - энергия {K21})\n"
    )
    try:
        message_file = await client.files.create(
            file=open("/app/numerology.pdf", "rb"), purpose="assistants"
        )

        thread = await client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "attachments": [
                        {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                    ],
                }
            ]
        )

        async with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                instructions=f"Please address the user as {user_name}.",
                event_handler=handler,
        ) as stream:
            await stream.until_done()
            
        return handler.response_text

    except Exception as e:
        print(f"Error in generate_gpt_response: {e}")
        return None
    
