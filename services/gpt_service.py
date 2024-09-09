import config
import tiktoken
from openai import OpenAI, AssistantEventHandler

client = OpenAI(api_key=config.OPENAI_API_KEY)


class EventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.response_text = None

    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_message_done(self, message) -> None:
        print("Message done called with message:", message)
        if hasattr(message, 'content'):
            print("Message content:", message.content)
            message_content = message.content[0].text

            annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
            citations = []
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f"[{index}] {cited_file.filename}")

            self.response_text = f"{message_content.value}\n\n" + "\n".join(citations)
        else:
            print("Message has no content")


assistant = client.beta.assistants.create(
    name="Numerology Assistant",
    instructions="You're an expert on the Matrix of Destiny. Use your knowledge base to answer questions based on the "
                 "provided book.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

vector_store = client.beta.vector_stores.create(name="Matrix of Destiny Book")

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
        f"1) Объем каждого пункта должен быть около 5-6 предложений.\n"
        f"2) Ты должен выдавать только интерпретации, но не включай ссылки на документы или индексы (например, "
        f"\"[18] matrix.pdf\".\n\n"
        f"3) В тексте ничего не выделяй жирным и курсивом."


        f"Порядок трактования расклада:\n\n"

        f"1) Личные качества:\n"
        f"1. Характер человека : Энергия {A}\n"
        f"Это характер человека, код личной силы, зона комфорта. От центра расходятся лучи к другим энергиям, "
        f"а это значит, что если центральная энергия в плюсе, то она максимально раскрывает и подпитывает все "
        f"остальные, отвечающие за различные сферы жизни. И наоборот – минусовой центр будет тянуть на дно все "
        f"остальные энергии.\n"
        f"2. Портрет личности: Энергия {X}\n"
        f"Это наши личные качества. Они от рождения даются нам в плюсе – это связь с нашей душой. Это компас нашей "
        f"души. Через портрет личности мы взаимодействуем с миром: общаемся, работаем, реализуем свой потенциал, "
        f"раскрываем свои таланты, отдыхаем, находимся в потоке и испытываем счастье и удовлетворение от жизни.\n"
        f"3. Высшая суть: Внутренний потенциал – Энергия {Y}, Талант от бога – Энергия {Y2}, Навык прошлого – Энергия {Y3}\n"
        f"В этом канале энергии показывают то позитивное, что было взято из прошлых воплощений, таланты, навыки, "
        f"опыт. Эта зона рассказывает о том, что человека вдохновляет, а от чего он впадает в депрессию.\n"
        f"Трактовки данных энергий находятся на 48-50 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"

        f"2) Предназначение:\n"
        f"1. Личное предназначение: энергия {LP}\n"
        f"2. Социальное предназначение: энергия {SP}\n"
        f"3. Духовное предназначение: энергия {DP}\n"
        f"4. Планетарное предназначение: энергия {PP}\n"
        f"Трактовки данных арканов находятся на 53-59 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"

        f"3) Детско-родительские отношения:\n"
        f"1. Для чего душа пришла к родителям – энергия {X}\n"
        f"Трактование находится на 62-66 страницах книги.\n"
        f"2. Задача отношений – энергия {X2}\n"
        f"Трактование находится на 67-70 страницах книги.\n"
        f"3. Ошибки во взаимоотношениях с родителями и своими детьми – энергия {X3}\n"
        f"Трактование находится на 71-74 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"

        f"4) Таланты:\n"
        f"1. Талант от бога – энергия {Y2}\n"
        f"Каким талантом от Бога вы обладаете. Раскрыв его, вы сможете прийти к выполнению своих трех предназначений. "
        f"Даже выбор профессии или сферы деятельности может быть направлен на развитие вашего таланта. Взяв за основу "
        f"энергии финансового канала текущего воплощения и талант от Бога – вы не только достигнете успеха в "
        f"самореализации, но и придете к высокому уровню дохода.\n"
        f"2. Внутренний потенциал: энергия {Y}\n"
        f"3. Навык прошлого: энергия {Y3}\n"
        f"Трактовка энергий находится на 142-170 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"

        f"5) Родовые программы:\n"
        f"1. Духовные задачи – энергии {B}, {C}\n"
        f"2. Материальные задачи – энергии {E}, {D}\n"
        f"Трактовка значений энергии находится на 77-82 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"

        f"6) Кармический хвост:\n"
        f"Кармический хвост: Энергии {G3}, {G2}, {G}\n"
        f"Кармический хвост – это тот багаж, который человек принес из прошлого воплощения. Это те задачи, "
        f"которые человек не успел решить в прошлом воплощении, и они будут влиять на нашу реальность.\n"
        f"Трактовка кармических хвостов находится на 84-99 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"

        f"7) Главный кармический урок души – энергия {G}\n"
        f"Трактовка значения находится на 102-103 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"
        f"8) Отношения:\n"
        f"1. Отношения в прошлом: энергия {G3}\n"
        f"Этот аркан говорит о самом худшем, что Вы делали в отношениях с людьми в предыдущем воплощении и "
        f"соответственно по старой памяти можете это повторять.\n"
        f"2. Как отношения влияют на финансы: энергия {A2}\n"
        f"Показывает то, как отношения влияют на финансы и наоборот.\n"
        f"3. Кармические отношения: энергия {A3}\n"
        f"Он показывает, что вам досталось кармически в этой жизни, что будет основополагающим в ваших отношениях в "
        f"этот раз.\n"
        f"Трактовка энергий находится на 142-170 страницах книги. Прежде чем перейти к следующему разделу напиши \"---\".\n\n"

        f"9) Деньги:\n"
        f"1. Как заработали деньги в прошлом – Энергия {Z3}\n"
        f"Показывает, как зарабатывали деньги в прошлом воплощении. Это подсказка на текущую жизнь. Можете начинать "
        f"свою деятельность с профессии по этому аркану. Но важно вывести его в плюс, чтобы доход рос, а не был в "
        f"отработку и тем самым деньги не утекали сквозь пальцы.\n"
        f"Трактовка энергии находится на 142-170 страницах книги.\n"
        f"2. Дополнительные возможности – энергия {A2}\n"
        f"Показывает дополнительные возможности, качества, которые в плюсе приведут вас к увеличению финансового "
        f"потока и дополнительно показывает совместную проработку для пары в плане финансов.\n"
        f"Трактовка энергии находится на 142-170 страницах книги.\n"
        f"3. Сферы высокого финансового потока – энергия {A1}\n"
        f"Это основной показатель наиболее благоприятной сферы для высокого финансового потока. Но и дополнительно "
        f"знак – на что тратить часть денег.\n"
        f"Трактовка энергии находится на 116-125 страницах книги.\n\n"
    )

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

    with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=f"Please address the user as {user_name}.",
            event_handler=handler,
    ) as stream:
        stream.until_done()

    return handler.response_text

