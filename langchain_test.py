from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv


load_dotenv()


class Review(BaseModel):
    mood: Literal["正面", "中性", "負面", "極度生氣", "極度好評"] = Field(
        description="使用的分析中呈現的使用者情緒."
    )
    user_name: str = Field(description="使用者名稱.")
    follow_up_question: str = Field(description="店家可能的下一步行動")


# prompt_template = PromptTemplate.from_template(
#     "以下是一個產品的回顧: {review}. 請分析使用者對這個產品的評價. 使用者名稱: {user_name}."
# )


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一個分析使用者對產品評價的專家. 你只能以 JSON 格式回覆: {format_instructions}",
        ),
        ("user", "品的回顧: {review}, 使用者名稱: {user_name}"),
    ]
)

model = ChatOpenAI(model="gpt-4.1")

parser = PydanticOutputParser(pydantic_object=Review)


# model_with_structured_output = model.with_structured_output(Review)
# model.with_structured_output(Review) 是比較新的寫法, 可以完全省略 "你只能以 JSON 格式回覆: {format_instructions}"的描述
chain = prompt_template | model | parser


ret = chain.invoke(
    {
        "user_name": "小明",
        "review": "需要等快2小時,赤豆鬆糕很美味,軟糯香甜不膩,千層糕也好吃,抄手醬汁一流.兒童椅高度不可調整有點不便,服務友善.",
        "format_instructions": parser.get_format_instructions(),
    }
)

# 以下請自行測試
# chain.invoke()
# chain.ainvoke()
# chain.batch()
# chain.abatch()
# chain.stream()
# chain.astream()


print(ret.mood)
print(ret.user_name)
print(ret.follow_up_question)

ret2 = chain.invoke(
    {
        "user_name": "小美",
        "review": "沒吃過這麼難吃的店, 絕對不會再來, 氣都氣飽了.",
        "format_instructions": parser.get_format_instructions(),
    }
)

print(ret2.mood)
print(ret2.user_name)
print(ret2.follow_up_question)


ret3 = chain.invoke(
    {
        "user_name": "小王",
        "review": "如神仙一般的美味, 太棒了!!!",
        "format_instructions": parser.get_format_instructions(),
    }
)

print(ret3.mood)
print(ret3.user_name)
print(ret3.follow_up_question)

pass
