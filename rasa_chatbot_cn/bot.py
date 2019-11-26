# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings
import sys

from rasa.core.actions import Action
from rasa.core.agent import Agent
# from rasa_core.channels.console import ConsoleInputChannel
from rasa.core.channels.console import CmdlineInput
from rasa.core.events import SlotSet
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.policies.keras_policy import KerasPolicy
from rasa.core.policies.memoization import MemoizationPolicy

logger = logging.getLogger(__name__)

support_search = ["消费", "流量"]

sys.path.append("./components")
sys.path.append("./policy")

def extract_item(item):
    """
    check if item supported, this func just for lack of train data.
    :param item: item in track, eg: "流量"、"查流量"
    :return:
    """
    if item is None:
        return None
    for name in support_search:
        if name in item:
            return name
    return None


class ActionSearchConsume(Action):
    def name(self):
        return 'action_search_consume'

    def run(self, dispatcher, tracker, domain):
        item = tracker.get_slot("item")
        item = extract_item(item)
        if item is None:
            dispatcher.utter_message("您好，我现在只会查话费和流量")
            dispatcher.utter_message("你可以这样问我：“帮我查话费”")
            return []

        time = tracker.get_slot("time")
        if time is None:
            dispatcher.utter_message("您想查询哪个月的消费？")
            return []
        # query database here using item and time as key. but you may normalize time format first.
        dispatcher.utter_message("好，请稍等")
        if item == "流量":
            dispatcher.utter_message("您好，您{}共使用{}二百八十兆，剩余三十兆。".format(time, item))
        else:
            dispatcher.utter_message("您好，您{}共消费二十八元。".format(time))
        return []


class MobilePolicy(KerasPolicy):
    def model_architecture(self, num_features, num_actions, max_history_len):
        """Build a Keras model and return a compiled model."""
        from keras.layers import LSTM, Activation, Masking, Dense
        from keras.models import Sequential

        n_hidden = 32  # size of hidden layer in LSTM
        # Build Model
        batch_shape = (None, max_history_len, num_features)

        model = Sequential()
        model.add(Masking(-1, batch_input_shape=batch_shape))
        model.add(LSTM(n_hidden, batch_input_shape=batch_shape))
        model.add(Dense(input_dim=n_hidden, output_dim=num_actions))
        model.add(Activation("softmax"))

        model.compile(loss="categorical_crossentropy",
                      optimizer="adam",
                      metrics=["accuracy"])

        logger.debug(model.summary())
        return model


# def train_dialogue(domain_file="mobile_domain.yml",
#                    model_path="projects/dialogue",
#                    training_data_file="data/mobile_story.md"):
#     agent = Agent(domain_file,
#                   policies=[MemoizationPolicy(), KerasPolicy()])
#
#     training_data = agent.load_data(training_data_file)
#     agent.train(
#         training_data,
#         epochs=200,
#         batch_size=16,
#         augmentation_factor=50,
#         validation_split=0.2
#     )
#
#     agent.persist(model_path)
#     return agent
#
# def train_nlu():
#     # from rasa_nlu.converters import load_data
#     from rasa_nlu_gao.training_data import load_data
#     # from rasa_nlu.config import RasaNLUConfig
#     from rasa_nlu_gao import config as RasaNLUConfig
#     from rasa_nlu_gao.model import Trainer
#
#     training_data = load_data("data/mobile_nlu_data.json")
#     # trainer = Trainer(RasaNLUConfig("mobile_nlu_model_config.json"))
#     trainer = Trainer(RasaNLUConfig.load("ivr_chatbot.yml"))
#     trainer.train(training_data)
#     model_directory = trainer.persist("models/", project_name="ivr", fixed_model_name="demo")
#
#     return model_directory
#
# def run_ivrbot_online(input_channel=CmdlineInput(),
#                       interpreter=RasaNLUInterpreter(r"models/nlu"),
#                       domain_file="domain.yml",
#                       training_data_file="data/nlu"):
#     agent = Agent(domain_file,
#                   policies=[MemoizationPolicy(), KerasPolicy()],
#                   interpreter=interpreter)
#
#     training_data = agent.load_data(training_data_file)
#     agent.train_online(training_data,
#                        input_channel=input_channel,
#                        batch_size=16,
#                        epochs=200,
#                        max_training_samples=300)
#
#     return agent


def run(serve_forever=True):
    agent = Agent.load("models/core",
                       interpreter=RasaNLUInterpreter("models/nlu"))

    if serve_forever:
        agent.handle_channel(CmdlineInput())
    return agent


##############测试###############
def Load_model():
    from rasa.utils.endpoints import EndpointConfig
    #加载Rasa Nlu模型和Rasa Core模型
    # agent = Agent.load("models/core",
    #                    interpreter=RasaNLUInterpreter("models/nlu"))
    agent = Agent.load(model_path="./models",
                       action_endpoint=EndpointConfig(url="http://localhost:5055/webhook"))
    return agent

async def get_res(agent,text):
    try:
        # res = agent.handle_message(text)
        res= await agent.handle_text(text)
        return res
    except Exception as e:
        print(e)

import asyncio
def get_ans(agent,text):
    # new_loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(get_res(agent, text))
    print(response)
    return response

if __name__ == "__main__":
    agent=Load_model()
    ans=get_ans(agent,"查话费")
    print(ans)
    # logging.basicConfig(level="INFO")
    #
    # parser = argparse.ArgumentParser(
    #     description="starts the bot")
    #
    # parser.add_argument(
    #     "task",
    #     choices=["train-nlu", "train-dialogue", "run", "online_train"],
    #     help="what the bot should do - e.g. run or train?")
    # task = parser.parse_args().task

    # decide what to do based on first parameter of the script
    # if task == "train-nlu":
    #     train_nlu()
    # elif task == "train-dialogue":
    #     train_dialogue()
    # elif task == "run":
    #     run()
    # elif task == "online_train":
    #     run_ivrbot_online()
    # else:
    #     warnings.warn("Need to pass either 'train-nlu', 'train-dialogue' or "
    #                   "'run' to use the script.")
    #     exit(1)
