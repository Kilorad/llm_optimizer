import re

class LLM_optimizer:
    def __init__(self, creator_bot, lang='only in English', eval_len=130, imporvement_len=200, eval_temp=0.1, improve_temp=1.1):
        self.creator_bot = creator_bot
        self.lang = lang
        self.imporvement_len = imporvement_len
        self.eval_len = eval_len
        self.eval_temp = eval_temp
        self.improve_temp = improve_temp
        self.result = {}
    def evaluate_response(self, response, success_criteria, initial_task, n_tokens=100):
        feedback = []
        total_quality_score = 0
        num_criteria = len(success_criteria)

        for criterion in success_criteria:
            evaluation_prompt = f"Есть задача: {initial_task}\n\n Есть ответ:{response}\n\n Оцени следующий ответ по критерию: '{criterion}'. Какую оценку ты поставил бы от 0 до 100 и почему? Оценка ({self.lang}):"
            evaluation_result = self.creator_bot.create_text(evaluation_prompt, False, max_tokens=n_tokens, temp=self.eval_temp)

            # Предполагаем, что результат содержит и оценку, и пояснение
            # Разделим результат на оценку и объяснение

            # Используем регулярное выражение для поиска оценки
            score_match = re.search(r'(\d+(\.\d+)?)', evaluation_result)  # Ищем число с возможной десятичной точкой

            if score_match:
                score = float(score_match.group(0))  # Получаем найденное число
            else:
                score = 0.0  # По умолчанию, если нет совпадений, устанавливаем оценку в 0

            # Извлекаем критику, оставив оставшуюся часть строки
            critique = evaluation_result
            total_quality_score += score

            feedback.append({
                'criterion': criterion,
                'score': score,
                'critique': critique.strip()
            })

        # Рассчитываем среднюю оценку
        average_quality_score = total_quality_score / num_criteria if num_criteria > 0 else 0

        return {'quality': average_quality_score, 'feedback': feedback}

    def improve_response(self, response, feedback, initial_task, n_tokens=220, temp=0.8):
        # Объединяем критику и создаем промт для улучшения
        critique_notes = "\n".join([f"Критика по критерию '{f['criterion']}': {f['critique']}" for f in feedback])

        improvement_prompt = f"Есть задача: {initial_task}\n\n Есть ответ:{response}\n\n Напиши лучший ответ с учетом этой критики (не пиши свою оценку ответа, только улучшенный ответ!):\n{critique_notes}\nРазмер поля ввода {int(n_tokens/3)} слов\nОтвет ({self.lang}):"
        improved_response = self.creator_bot.create_text(improvement_prompt, False, max_tokens=n_tokens, temp=temp)
        improved_response = self.creator_bot.filtration(improved_response)
        return improved_response

    def iterative_improvement(self, initial_task, success_criteria, max_iterations=10, desired_quality=8.0, temp=0.8):
        # Создание начального ответа
        initial_prompt = f"Сформулируй начальный ответ на следующую задачу: {initial_task}. Ответ ({self.lang}):"
        current_response = self.creator_bot.create_text(initial_prompt, False, max_tokens=self.imporvement_len, temp=0.1)
        current_response = self.creator_bot.filtration(current_response)

        iteration_count = 0

        best_result = {'quality':0, 'value':'', 'feedback':''}
        while iteration_count < max_iterations:
            # Оценка текущего ответа на основе критериев успеха
            feedback = self.evaluate_response(current_response, success_criteria, initial_task, n_tokens=self.eval_len)

            print("****current_response", current_response)
            print("-----feedback['feedback']", feedback['feedback'])
            # Проверка, достигнуто ли желаемое качество
            if feedback['quality'] >= desired_quality:
                print(f"Достигнуто желаемое качество: {feedback['quality']}.")
                break
            if feedback['quality'] > best_result['quality']:
                best_result['value'] = current_response
                best_result['quality'] = feedback['quality']
                best_result['feedback'] = feedback['feedback']
                print('UPDATE', feedback['quality'], best_result['quality'])
                self.result = best_result
            else:
                current_response = best_result['value']
                feedback['feedback'] = best_result['feedback']
                print('REJECT', feedback['quality'], best_result['quality'])


            # Улучшение ответа на основе полученной обратной связи
            current_response = self.improve_response(current_response, feedback['feedback'], initial_task, self.imporvement_len, self.improve_temp)
            iteration_count += 1

        return best_result['value']  # Возвращение наиболее качественного ответа