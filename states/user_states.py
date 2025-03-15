"""
[RU]
Модуль определения состояний пользователя в диалоге с ботом.

Содержит классы для управления состояниями в процессе интервью
и просмотра примеров работ.

[EN]
Module for defining user states in dialogue with bot.

Contains classes for managing states during interview process
and viewing work examples.
"""

from aiogram.fsm.state import State, StatesGroup


class Interview(StatesGroup):
    """
    [RU]
    Группа состояний для процесса интервью.

    Attributes:
        name (State): Состояние ввода имени
        question (State): Состояние ответа на вопросы анкеты
        phone (State): Состояние ввода номера телефона

    [EN]
    State group for interview process.

    Attributes:
        name (State): Name input state
        question (State): Questionnaire answering state
        phone (State): Phone number input state
    """
    name = State()
    question = State()
    phone = State()


class Reference(StatesGroup):
    """
    [RU]
    Группа состояний для просмотра примеров работ.

    Attributes:
        view (State): Состояние просмотра примеров

    [EN]
    State group for viewing work examples.

    Attributes:
        view (State): Examples viewing state
    """
    view = State()