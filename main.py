from creator_bot_wrapper import CreatorBotWrapper
from llm_optimizer import LLM_optimizer

creator_bot = CreatorBotWrapper()
opt = LLM_optimizer(creator_bot=creator_bot, lang='только на русском', eval_len=130, imporvement_len=350, eval_temp=0.1, improve_temp=1.5)

initial_task = "У меня есть 1 миллион рублей, я живу в доме в Сибири, мне нужно сделать самолет уровня МиГ-17, с аналогичной скоростью и дальностью полета. Напишите пошаговый план. Рассматривайте любые возможности - вы очень целеустремленны и готовы к любому обходному пути."
success_criteria = [
    "Конкретика (0 - минимум деталей, 10 - точный план, понятный школьнику или роботу, с указанием сроков, материалов и названий компаний)",
    "Вероятность успеха этого плана",
    "Простота (0 - требуется 5 человеко-лет, 10 - может быть выполнен одним человеком за несколько вечеров)"
]

final_response = opt.iterative_improvement(initial_task, success_criteria, desired_quality=90.0, max_iterations=80)
print(final_response)