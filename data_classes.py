
class TicketData:
    def __init__(self):
        self.ticket_type = ""
        self.departure_station = ""
        self.arrival_station = ""
        self.seat_type = ""
        self.seat_number = ""
        self.train_number = ""
        self.via_route = ""
        self.ticket_number = 0

    def set_ticket(self,ticket_dict):
        self.ticket_type = ticket_dict["券種"]
        self.departure_station = ticket_dict["出発駅"]
        self.arrival_station = ticket_dict["到着駅"]
        self.seat_type = ticket_dict["席種"]
        self.seat_number = ticket_dict["席番号"]
        self.train_number = ticket_dict["電車番号"]
        self.via_route = ticket_dict["経由"]
        return self


class TicketBox:
    def __init__(self):
        self.basicFare_ticket = []
        self.superExpress_basicFare_ticket = []
        self.ltdFare_ticket = []
        self.superExpressFare_ticket = []
        self.reservation_ticket = []
        self.superExpress_reservation_ticket = []
        self.receipt = []
        self.slip = []
        self.unknown = []
        self.baseInfo = []

    def putTicketIntheBox(self,ticket_data:TicketData):
        unknow = True
        # basicInfo = {"ticket_number":ticket_data.ticket_number, "ticket_type":ticket_data.ticket_type,
        #              "departure_station":ticket_data.departure_station, "arrival_station":ticket_data.arrival_station}
        # self.baseInfo.append(basicInfo)
        ticket_type = ticket_data.ticket_type
        # 乗車券判定
        try:
            if(("乗車券(幹)" in ticket_type) or (("新幹線" in ticket_type) and ("乗車券" in ticket_type)) or ("乗車券（幹）" in ticket_type)):
                self.superExpress_basicFare_ticket.append(ticket_data)
                unknow = False
            elif("乗車券" in ticket_type):
                self.basicFare_ticket.append(ticket_data)
                unknow = False
            # 特急券判定
            if(("新幹線" in ticket_type) and ("特急券" in ticket_type)):
                self.superExpressFare_ticket.append(ticket_data)
                unknow = False
            elif("特急券" in ticket_type):
                self.ltdFare_ticket.append(ticket_data)
                unknow = False

            # 指定券
            if (("新幹線" in ticket_type) and ("指定券" in ticket_type)):
                self.superExpress_reservation_ticket.append(ticket_data)
                unknow = False
            elif ("指定券" in ticket_type):
                self.reservation_ticket.append(ticket_data)
                unknow = False

            # 領収書
            if("領収書" in ticket_type):
                self.receipt.append(ticket_data)
                unknow = False

            if("利用票" in ticket_type):
                self.slip.append(ticket_data)
                unknow = False

            if(unknow):
                self.unknown.append(ticket_data)
        except:
            pass

        return self

    def getAllBasicFareTicket(self):
        total_basicFare = self.basicFare_ticket + self.superExpress_basicFare_ticket
        return len(total_basicFare), total_basicFare

    def check_only_receipt(self) -> bool:
        num_basic = len(self.basicFare_ticket)
        num_super_basic = len(self.superExpress_basicFare_ticket)
        num_ltdFare = len(self.ltdFare_ticket)
        num_superExpFare = len(self.superExpressFare_ticket)
        num_reservation_ticket = len(self.reservation_ticket)
        num_superExpress_reservation = len(self.superExpress_reservation_ticket)
        num_unknown = len(self.unknown)
        nun_ticket = num_basic + num_super_basic + num_ltdFare + num_superExpFare + num_reservation_ticket + num_superExpress_reservation + num_unknown
        if((len(self.receipt) != 0) and nun_ticket == 0):
            return True
        else:
            return False

    def set_baseInfo(self):
        ticket_number_dict = {}
        for basicFare in self.basicFare_ticket:
            ticket_number = int(basicFare.ticket_number)
            basicInfo = {"ticket_type": "乗車券", "departure_station": basicFare.departure_station, "arrival_station": basicFare.arrival_station}
            ticket_number_dict[ticket_number] = basicInfo

        for ltdFare in self.ltdFare_ticket:
            ticket_number = int(ltdFare.ticket_number)
            if(ticket_number in ticket_number_dict):
                ticket_number_dict[ticket_number]["ticket_type"] = "乗車券・特急券"
            else:
                ticket_number_dict[ticket_number] = {"ticket_type": "特急券", "departure_station": ltdFare.departure_station, "arrival_station": ltdFare.arrival_station}

        for superExpBasicFare in self.superExpress_basicFare_ticket:
            ticket_number = int(superExpBasicFare.ticket_number)
            basicInfo = {"ticket_type": "乗車券（幹）", "departure_station": superExpBasicFare.departure_station,
                         "arrival_station": superExpBasicFare.arrival_station}
            ticket_number_dict[ticket_number] = basicInfo

        for superExpFare in self.superExpressFare_ticket:
            ticket_number = int(superExpFare.ticket_number)
            if(ticket_number in ticket_number_dict):
                ticket_number_dict[ticket_number]["ticket_type"] = "乗車券・新幹線特急券"
            else:
                ticket_number_dict[ticket_number] = {"ticket_type": "新幹線特急券","departure_station": superExpFare.departure_station,"arrival_station": superExpFare.arrival_station}

        for reservation_ticket in self.reservation_ticket:
            ticket_number = int(reservation_ticket.ticket_number)
            basicInfo = {"ticket_type": "指定券", "departure_station": reservation_ticket.departure_station,
                         "arrival_station": reservation_ticket.arrival_station}
            ticket_number_dict[ticket_number] = basicInfo

        for superExpress_reservation_ticket in self.superExpress_reservation_ticket:
            ticket_number = int(superExpress_reservation_ticket.ticket_number)
            basicInfo = {"ticket_type": "新幹線指定券", "departure_station": superExpress_reservation_ticket.departure_station,
                         "arrival_station": superExpress_reservation_ticket.arrival_station}
            ticket_number_dict[ticket_number] = basicInfo

        for receipt in self.receipt:
            ticket_number = int(receipt.ticket_number)
            basicInfo = {"ticket_type": "領収書",
                         "departure_station": receipt.departure_station,
                         "arrival_station": receipt.arrival_station}
            ticket_number_dict[ticket_number] = basicInfo

        for slip in self.slip:
            ticket_number = int(slip.ticket_number)
            basicInfo = {"ticket_type": "領収書",
                         "departure_station": slip.departure_station,
                         "arrival_station": slip.arrival_station}
            ticket_number_dict[ticket_number] = basicInfo

        for num, _ in enumerate(ticket_number_dict):
            try:
                ticket_info = ticket_number_dict[num+1]
                ticket_info["ticket_number"] = str(num+1)
                self.baseInfo.append(ticket_info)
            except:
                pass
