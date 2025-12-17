import tools
from gpt_Setter import GPTSetter
import json
import ast
from data_classes import TicketData, TicketBox
from deep_translator import GoogleTranslator

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# print(BASE_DIR)

class TicketOCRService:
    def __init__(self):
        self.stations_dictionary = {}
        self.language = ""

    @staticmethod
    def fallback_translate_place(name: str, target_lang: str) -> str:
        lang_cn_dict = {"zh":"zh-Hans","zh-TW":"zh-Hant"}
        if(target_lang in lang_cn_dict.keys()):
            target_lang = lang_cn_dict[target_lang]
        try:
            text = (
                f"{name}. "
                "This is a geographic place name. "
                "Do not translate the meaning."
            )
            result = GoogleTranslator(
                source="ja",
                target=target_lang
            ).translate(text)

            return result.split(".")[0].strip()
        except Exception:
            return name
    def ticket_ocr_service(self, imgs_b64_list,language,stations_dictionary,location,ticket_type,guidanceBooks):
        tool = tools.Tools()
        self.stations_dictionary = stations_dictionary
        api_key_filePath = "---"
        # api_key_filePath = "/Users/szchandler/Desktop/localCode/Ticket_OCR/Backend_Ticket_JR/setting/api_key.json"
        chat_basic_setting_filePath = "{}/setting/gpt_basic_setting.json".format(BASE_DIR)
        chat_setting_filePath = "{}/setting/api_chat_setting.json".format(BASE_DIR)
        gpt_setter = GPTSetter(api_key_filePath, chat_basic_setting_filePath)

        if(language == "ja"):
            guidanceBook = guidanceBooks["jp"]
        elif(language == "en"):
            guidanceBook = guidanceBooks["en"]
        elif (language == "zh-Hans"):
            guidanceBook = guidanceBooks["cn"]
            language = "zh"
        elif (language == "zh-Hant"):
            guidanceBook = guidanceBooks["tw"]
            language = "zh-TW"
        elif (language == "zh-HK"):
            guidanceBook = guidanceBooks["hk"]
            language = "zh-TW"
        elif (language == "ko"):
            guidanceBook = guidanceBooks["ko"]
        elif (language == "es"):
            guidanceBook = guidanceBooks["es"]

        self.language = language

        ticket_data_list = {}
        tickets_box = TicketBox()
        for num,imgs_b64 in enumerate(imgs_b64_list):
            ticket_data = gpt_setter.getText(chat_setting_filePath, imgs_b64,language)
            print(ticket_data)
            ticket_data_dict = self.normalize_dict(ast.literal_eval(ticket_data))
            ticket_data_list[num] = ticket_data_dict
            ticketData = TicketData()
            ticketData = ticketData.set_ticket(ticket_data_dict)
            ticketData.ticket_number = num + 1
            tickets_box.putTicketIntheBox(ticketData)
        # 此处以下为业务逻辑

        return_data_dict = {}
        return_text_list = self.itinerary_confirmation(location=location,ticket_type=ticket_type,tickets_box=tickets_box,guidanceBook=guidanceBook,language=language,stations_dictionary=stations_dictionary)
        for num, return_text in enumerate(return_text_list):
            num_str = str(num)
            return_data_dict[num_str] = {"respone":return_text}
        return return_data_dict
        # return {"0":{"respone":return_text}}

    def normalize_dict(self, d: dict) -> dict:
        return {k: (None if v == "None" else v) for k, v in d.items()}

    def check_stations_dictionary(self,station_name)->str:
        language = self.language
        if(language == "ja"):
            return station_name
        else:
            try:
                stations_dictionary = self.stations_dictionary
                return stations_dictionary[station_name][language]
            except KeyError:
                return self.fallback_translate_place(station_name, self.language)

    def function_code_8(self,basicFareTicket,guidance):
        ticket_num = basicFareTicket.ticket_number
        dep_station = self.check_stations_dictionary(basicFareTicket.departure_station)
        arrival_station = self.check_stations_dictionary(basicFareTicket.arrival_station)
        return_sub_texts = guidance.format(dep_station, ticket_num, dep_station,
                                           arrival_station) + "\n"
        return return_sub_texts

    def ticket_info_collection2string(self,ticketInfoBoxs)->str:
        if(len(ticketInfoBoxs)==0):
            return "No tickets information"
        elif(len(ticketInfoBoxs)==1):
            return ticketInfoBoxs[0]
        else:
            ret_str = ','.join(str(x) for x in ticketInfoBoxs)
            return ret_str

    def outPutTicketInfo(self,input_word, target_lang) -> str:
        return ""

    # 行程判定器，讲输入的车票汇总判定
    def itinerary_confirmation(self,location,ticket_type,tickets_box,guidanceBook,language,stations_dictionary)->[str]:
        return_texts = []
        # 处理基础信息
        tickets_box.set_baseInfo()
        basicInfoList = tickets_box.baseInfo
        ticket_basic_infos = []
        for basicInfo in basicInfoList:
            ticket_number = basicInfo["ticket_number"]
            ticket_type_info = self.check_stations_dictionary(basicInfo["ticket_type"])
            ticket_departure_station_info = self.check_stations_dictionary(basicInfo["departure_station"])
            ticket_arrival_station_info = self.check_stations_dictionary(basicInfo["arrival_station"])

            return_sub_text = guidanceBook["998"].format(ticket_number,ticket_type_info,ticket_departure_station_info,ticket_arrival_station_info)
            ticket_basic_infos.append(return_sub_text)
            # basicInfoStr += "\n"
        basicInfoStr = "\n".join(ticket_basic_infos)
        return_texts.append(guidanceBook["999"].format(basicInfoStr))

        if(ticket_type == "normal_ticket"):
            if(location == "station_gate_outside"):
                # Group A
                num_basicFare, basicFareTickets = tickets_box.getAllBasicFareTicket()
                if(num_basicFare > 0):
                    # code 1 or 3
                    if(len(tickets_box.superExpressFare_ticket) == 0):
                        for basicFareTicket in basicFareTickets:
                            guidance = guidanceBook["1"]

                            ticket_num = basicFareTicket.ticket_number
                            dep_station = self.check_stations_dictionary(basicFareTicket.departure_station)
                            arrival_station = self.check_stations_dictionary(basicFareTicket.arrival_station)

                            return_sub_texts = guidance.format(dep_station, ticket_num, dep_station,
                                                               arrival_station) + "\n"
                            return_texts.append(guidanceBook['696'].format(return_sub_texts))
                    else:
                        for basicFareTicket in basicFareTickets:
                            for superExpTicket in tickets_box.superExpressFare_ticket:
                                if((basicFareTicket.departure_station == superExpTicket.departure_station) and (basicFareTicket.ticket_number != superExpTicket.ticket_number)):
                                    # code 3
                                    guidance = guidanceBook["1"]
                                    departure_station = self.check_stations_dictionary(superExpTicket.departure_station)
                                    arrival_station = self.check_stations_dictionary(superExpTicket.arrival_station)

                                    return_sub_texts = (guidanceBook["1"].format(departure_station,superExpTicket.ticket_number,departure_station,arrival_station)
                                                            + "\n" + guidanceBook["3"].format(superExpTicket.ticket_number,departure_station,arrival_station)+"\n")
                                    # return_texts += return_sub_texts
                                    return_texts.append(guidanceBook['696'].format(return_sub_texts))
                                else:
                                    # code 1
                                    guidance = guidanceBook["1"]

                                    ticket_num = basicFareTicket.ticket_number
                                    dep_station = self.check_stations_dictionary(basicFareTicket.departure_station)
                                    arrival_station = self.check_stations_dictionary(basicFareTicket.arrival_station)

                                    return_sub_texts = guidance.format(dep_station, ticket_num, dep_station, arrival_station) + "\n"
                                    return_texts.append(guidanceBook['696'].format(return_sub_texts))
                else:
                    # code 2
                    return_sub_texts = guidanceBook["2"]
                    return_texts.append(guidanceBook['699'].format(return_sub_texts))
                    if(tickets_box.check_only_receipt()):
                        return_texts.append(guidanceBook['698'].format(guidanceBook["994"]))
                    else:
                        return_texts.append(guidanceBook['697'].format(guidanceBook["995"]))
            elif(location == "station_inside_transfer"):
                # Group B
                num_basicFare, basicFareTickets = tickets_box.getAllBasicFareTicket()
                if(num_basicFare == 0):
                    # code 5
                    return_sub_texts = guidanceBook["5"]
                    return_texts.append(guidanceBook['699'].format(return_sub_texts))
                    pass
                else:
                    superExpTickets = tickets_box.superExpressFare_ticket
                    if(len(superExpTickets) == 0):
                        # code 4
                        return_sub_texts = guidanceBook["4"]
                        return_texts.append(guidanceBook['699'].format(return_sub_texts))
                        pass
                    else:
                        ltdExpTickets = tickets_box.ltdFare_ticket
                        receipts = tickets_box.receipt
                        if((len(ltdExpTickets) == 0) and (len(receipts) == 0)):
                            # code 7
                            return_sub_texts = guidanceBook["7"]
                            return_texts.append(guidanceBook['696'].format(return_sub_texts))
                            pass
                        else:
                            return_sub_text = ""
                            # code 6
                            if(len(receipts) != 0):
                                for receipt in receipts:
                                    return_receipts_text = guidanceBook["997"].format(receipt.ticket_number)
                                    return_receipts_text = "{}\n".format(return_receipts_text)
                                    return_sub_text += return_receipts_text
                            if(len(ltdExpTickets) != 0):
                                for ltdExpTicket in ltdExpTickets:
                                    ticket_type = self.check_stations_dictionary(ltdExpTicket.ticket_type)
                                    ticket_departure_station = self.check_stations_dictionary(ltdExpTicket.departure_station)
                                    ticket_arrival_station = self.check_stations_dictionary(ltdExpTicket.arrival_station)
                                    return_LTD_text = guidanceBook["998"].format(ltdExpTicket.ticket_number,ticket_type,ticket_departure_station,ticket_arrival_station)
                                    return_LTD_text += "{}\n".format(return_LTD_text)
                                    return_sub_text += return_LTD_text
                            return_texts.append(guidanceBook["698"].format(guidanceBook["6"].format(return_sub_text)))
                            pass
                pass
            elif(location == "station_inside_exit_request"):
                # Group C
                num_basicFare, basicFareTickets = tickets_box.getAllBasicFareTicket()
                superExpTickets = tickets_box.superExpressFare_ticket
                if(num_basicFare >= 1):
                    # code 8
                    for basicFareTicket in basicFareTickets:
                        if(len(superExpTickets) > 0):
                            for superExpTicket in superExpTickets:
                                if((superExpTicket.arrival_station == basicFareTicket.arrival_station) and (superExpTicket.ticket_number!=basicFareTicket.ticket_number)):
                                    # code 10
                                    guidance = guidanceBook["10"]
                                    basicFareTicket_departure_station_info = self.check_stations_dictionary(basicFareTicket.departure_station)
                                    basicFareTicket_arrival_station_info = self.check_stations_dictionary(basicFareTicket.arrival_station)
                                    superExpTicket_departure_station_info = self.check_stations_dictionary(superExpTicket.departure_station)
                                    superExpTicket_arrival_station_info = self.check_stations_dictionary(superExpTicket.arrival_station)
                                    basicFareTicketNumber = basicFareTicket.ticket_number
                                    superExpTicketNumber = superExpTicket.ticket_number
                                    return_sub_text = guidance.format(basicFareTicket_arrival_station_info,basicFareTicketNumber,basicFareTicket_departure_station_info,basicFareTicket_arrival_station_info,superExpTicketNumber,superExpTicket_departure_station_info,superExpTicket_arrival_station_info)
                                    return_texts.append(guidanceBook["696"].format(return_sub_text))
                                else:
                                    return_sub_texts = self.function_code_8(basicFareTicket=basicFareTicket,guidance=guidanceBook["8"])
                                    return_texts.append(guidanceBook["696"].format(return_sub_texts))
                        else:
                            return_sub_texts = self.function_code_8(basicFareTicket=basicFareTicket,guidance=guidanceBook["8"])
                            return_texts.append(guidanceBook["696"].format(return_sub_texts))
                    return_texts.append(guidanceBook["698"].format(guidanceBook["996"]))
                else:
                    # code 9
                    return_texts.append(guidanceBook["699"].format(guidanceBook["9"]))
                    pass
                pass
            elif(location == "shinkansen_inside_transfer"):
                # Group D
                num_basicFare, basicFareTickets = tickets_box.getAllBasicFareTicket()
                superExpTickets = tickets_box.superExpressFare_ticket
                if(num_basicFare == 0):
                    # code 13
                    return_texts.append(guidanceBook["697"].format(guidanceBook['995']))
                    return_texts.append(guidanceBook["699"].format(guidanceBook['13']))
                    pass
                else:
                    if(len(superExpTickets) == 0):
                        # code 12
                        return_texts.append(guidanceBook["697"].format(guidanceBook['995']))
                        return_texts.append(guidanceBook["699"].format(guidanceBook['12']))
                    else:
                        pair_ticket_basic = []
                        pair_ticket_superExp = []
                        # code 11
                        for basicFareTicket in basicFareTickets:
                            ticket_number = basicFareTicket.ticket_number
                            departure_station = self.check_stations_dictionary(basicFareTicket.departure_station)
                            arrival_station = self.check_stations_dictionary(basicFareTicket.arrival_station)
                            pair_ticket_basic.append(guidanceBook["993"].format(ticket_number, departure_station, arrival_station))
                        for superExpTicket in superExpTickets:
                            ticket_number = superExpTicket.ticket_number
                            departure_station = self.check_stations_dictionary(superExpTicket.departure_station)
                            arrival_station = self.check_stations_dictionary(superExpTicket.arrival_station)
                            pair_ticket_superExp.append(guidanceBook["993"].format(ticket_number, departure_station, arrival_station))
                        basicTicketsInfo = self.ticket_info_collection2string(pair_ticket_basic)
                        superExpTicketInfo = self.ticket_info_collection2string(pair_ticket_superExp)
                        return_sub_text = guidanceBook['11'].format(basicTicketsInfo,superExpTicketInfo)
                        return_texts.append(guidanceBook["696"].format(return_sub_text))

            else:
                # Group Z
                return_texts.append(guidanceBook["699"].format(guidanceBook['14']))
                pass
        elif(ticket_type == "jr-pass"):
            # jr-pass 認識のみ、判定なし
            return_texts.append(guidanceBook["698"].format(guidanceBook["899"]))
            pass
        else:
            return_texts.append(guidanceBook["698"].format(guidanceBook["799"]))
            pass
        return return_texts
