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
        if hasattr(message, 'content'):
            message_content = message.content[0].text

            if message_content:

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
        name="Matrix of compatibility",
        instructions="You're an expert on the compatibility. Use your knowledge base to answer questions based on the provided book.",
        model="gpt-4o-2024-08-06",
        tools=[{"type": "file_search"}],
    )

    vector_store = await client.beta.vector_stores.create(name="Matrix of compatibility")

    file_paths = ["/app/compatibility.pdf"]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = await client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    assistant = await client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    return assistant

async def generate_gpt_response_com(user_name, values, assistant):
    handler = EventHandler()
    X = values.get('X')
    Y = values.get('Y')
    A = values.get('A')
    B = values.get('B')
    Z = values.get('Z')
    G = values.get('G')
    X3 = values.get('X3')
    C = values.get('C')
    A1 = values.get('A1')
    A2 = values.get('A2')

    prompt = (
        f"Чат, тебе необходимо составить личный расклад на основе загруженного файла.\n\n"
        f"1) Объем каждого пункта должен быть около 5-6 предложений.\n"
        f"2) Твоя задача интерпретировать энергию согласно ее значению в конкретной сфере, пример: Ты смотришь что в разделе “Для чего пара встретилась” стоит {Y} энергия, смотришь ее значение в загруженном файле и выдаешь интерпретацию для чего пара встретилась, согласно значению {Y} энергии, но не включай ссылки на документы или индексы (например, "
        f"\"[18] matrix.pdf\".\n\n"
        f"3) В тексте ничего не выделяй жирным и курсивом."
        f"4) Нигде в ответе не используй # и *.\n\n"

        
        f"Порядок трактования расклада:\n"
        f"Для чего пара встретилась, Энергия {Y}\n"
        f"Это положительный аспект пары, а также это точка, которая показывает нам, для чего семья создавалась, то есть для чего пара встретилась в плюсе. Она не несёт негативного подтекста, а лишь положительное значение. Хочу уточнить, что это не задача в глобальном смысле, а то, что паре нужно создать в своём союзе, почему произошло их знакомство. Даже если пара по остальным энергиям находится в минусе. Например, 3 - это рождение ребёнка, открытие бизнеса либо быстрое обретение материальных благ и статуса для обоих. 15-я энергия очень часто показывает выход из зависимости. Прежде чем перейти к следующему разделу напиши \"---\"."
        
        f"Как пара выглядит для других, Энергия {X}\n"
        f"Как пара проявляется для всех. Это то, что видит в паре внешнее окружение. То, как они проявляются или хотят, чтобы их видели во внешнем мире, своеобразный образ, который они транслируют для всех. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Общая атмосфера внутри пары, Энергия {A}\n"
        f"Точка A (центр матрицы) - общая атмосфера между партнёрами. Это то, что видят и чувствуют друг к другу партнёры. Это то, что внутри пары НЕ напоказ. В положительном ключе данная точка говорит о хорошей атмосфере между партнёрами, а в негативном ключе - об отрицательной атмосфере. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Что укрепляет союз, Энергия {B}\n"
        f"Данная точка в совместимости показывает нам, что наполняет пару, что помогает восстанавливать отношения, какие общие интересы у партнёров. Данная энергия показывает нам то, что соединяет супругов и семью в целом, на чём держится их брак. Данная точка читается в положительном аспекте, даже минусы. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Финансы, Энергия {Z}\n"
        f"Данная точка показывает отношение пары к материальному. Эта точка начинает материальную линию. В базовой матрице данная линия называется материальной кармой, но здесь она отвечает за отношение супругов к материальным вещам. Хозяйственность, ремонт, траты, секс, уход, накопления, распоряжение, наследственность и другое. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Через что достичь финансового благополучия, Энергия {A1}\n"
        f"Данная энергия показывает через что пара может достичь финансового благополучия. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Проблемы в финансах, Энергия {A2}\n"
        f"Энергия в целом отвечает за трудности, которые могут быть в паре в плане финансирования и дохода, а также что нужно сделать, чтобы этого избежать. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Желания и цели, Энергия {X3}\n"
        f"В контексте совместимости говорит нам о том, как партнёры (как единый организм) будут проявляться как родители. Как уважают друг друга, как поддерживают друг друга именно как родители. Можно даже сказать, это то, как их может видеть ребёнок. Какое у них поведение. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Задачи пары, Энергия {G}\n"
        f"Это точка, которая показывает основные проблемы и минусы пары. Какие основные задачи и испытания их ждут и через что им нужно будет пройти, чему научиться в этих отношениях. Данная точка начинается линию задач, в базовой матрице она называется кармический хвостик, но здесь можно назвать её просто задачей пары. Данная точка читается по большей части в минусовых значениях, но не забывайте о том, что и плюс может быть минусом. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        
        f"Трудности и недопонимания, Энергия {C}\n"
        f"Которая показывает, что может испортить отношения, в чём могут быть серьёзные конфликты и недопонимания. Эта точка показывает нам, в чём между партнёрами может быть недоговорённость, непринятие, что может быть не совсем понятно друг в друге."
    )
    try:
        message_file = await client.files.create(
            file=open("/app/compatibility.pdf", "rb"), purpose="assistants"
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
    
