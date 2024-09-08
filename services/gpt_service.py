import config
import tiktoken
from openai import OpenAI, AssistantEventHandler

client = OpenAI(api_key=config.OPENAI_API_KEY)


class EventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.response_text = None

    def on_text_created(self, text) -> None:
        print(f"\nassistant > Text created: {text}", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > Tool call created: {tool_call.type}", flush=True)

    def on_message_done(self, message) -> None:
        print("Message done called with message:", message)
        if hasattr(message, 'content'):
            print("Message content:", message.content)
            message_content = message.content[0].text
            print("Extracted message content:", message_content)

            annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
            citations = []
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f"[{index}] {cited_file.filename}")

            self.response_text = f"{message_content.value}\n\n" + "\n".join(citations)
            print("Updated response text:", self.response_text)
        else:
            print("Message has no content")


assistant = client.beta.assistants.create(
    name="Numerology Assistant",
    instructions="You are an expert numerology analyst. Use your knowledge base to answer questions based on the "
                 "provided book.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

vector_store = client.beta.vector_stores.create(name="Numerology Book")

file_paths = ["/app/matrix.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)


async def generate_gpt_response(user_name, values, handler):
    A = values.get('A')
    X = values.get('X')
    Y = values.get('Y')
    Y2 = values.get('Y2')
    Y3 = values.get('Y3')
    LP = values.get('LP')
    SP = values.get('SP')
    DP = values.get('DP')
    PP = values.get('PP')
    X2 = values.get('X2')
    X3 = values.get('X3')
    Z3 = values.get('Z3')
    A1 = values.get('A1')
    A2 = values.get('A2')
    A3 = values.get('A3')
    Z = values.get('Z')
    B = values.get('B')
    C = values.get('C')
    E = values.get('E')
    D = values.get('D')
    G3 = values.get('G3')
    G2 = values.get('G2')
    G = values.get('G')
    N = values.get('N')
    ZZ = values.get('ZZ')
    M = values.get('M')
    Zh = values.get('Zh')

    prompt = (
        f"Чат, тебе необходимо составить расклад на основе загруженного файла для каждой из категорий.\n\n"
        # Текст укорачен для краткости
    )

    print("Создание файла и потока сообщений...")

    message_file = client.files.create(
        file=open("/app/matrix.pdf", "rb"), purpose="assistants"
    )

    thread = client.beta.threads.create(
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

    print("Запуск потока сообщений...")

    with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=f"Please address the user as {user_name}.",
            event_handler=handler,  # Исправлено: передаем `handler` сюда
    ) as stream:
        print("Поток запущен, ожидание завершения...")
        stream.until_done()  # Этот метод должен завершиться, вызвав события

    print("Поток завершен.")
    return handler.response_text
