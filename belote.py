import random
import time
from spade.behaviour import FSMBehaviour, State
from spade import quit_spade
from spade.agent import Agent
from argparse import ArgumentParser
from spade import quit_spade

class Karta:
    def __init__(self, broj, znak):
        self.broj = broj
        self.znak = znak

    def __repr__(self):
        return f"{self.broj}{self.znak}"

class Igrac(Agent):
    def __init__(self, jid, password, ime):
        super().__init__(jid, password)
        self.karte = []
        self.bacena_karta = None
        self.ime = ime
        self.zvao_adut = False
        self.ima_zvanje_bele = False

    class PonasanjeKA(FSMBehaviour):
        async def on_start(self):
            print(f"Započinje ponašanje igrača: {self.agent.jid}")

        async def on_end(self):
            print(f"Završava ponašanje igrača:  {self.agent.jid}")

    class Cekaj(State):
        async def run(self):
            if self.agent.igra:
                self.set_next_state("Odigraj")
            else:
                time.sleep(1)
                self.set_next_state("Cekaj")

    class Odigraj(State):
        async def run(self):
            print(f"Na potezu je {self.agent.ime}")
            self.agent.igra=False
            self.odigraj()
            self.agent.odigrao=True
            self.set_next_state("Cekaj")

        def odigraj(self):
            if self.agent.runda < 8:
                karta = self.dohvatiKarteZaRundu()
            else:
                karta = self.agent.karte[0]
            oznaka_karte = str(karta)[-1]
            broj_karte = str(karta)[:-1]

            print(f"{self.agent.ime} baca kartu: {karta}")

            if oznaka_karte == self.agent.adut and (broj_karte == 'Q' or broj_karte == 'K') and self.agent.ima_zvanje_bele == True:
                print("-- Bela --")

            self.agent.bacena_karta=karta
            self.agent.baci_kartu(karta)

        def dohvatiKarteZaRundu(self):
            karte = self.agent.karte
            adut = self.agent.adut
            redoslijed = self.agent.redoslijed
            if redoslijed == 1:
                karta = self.provjeri_ima_li_glavni_adut(adut, karte)
                if karta is None:
                    karta = self.baci_najjacu_kartu_koja_nije_adut(adut, karte)
                    if karta is None:
                        karta = self.baci_bilo_koju_kartu_koja_nije_adut(adut, karte)
            elif redoslijed == 2:
                karta = self.provjeri_prethodno_bacenu_kartu(adut, karte)
            elif redoslijed == 3:
                karta = self.provjeri_prethodno_bacene_karte(adut, karte)
            else:
                karta = self.baci_zadnju_kartu(adut, karte)
            return karta

        def provjeri_ima_li_glavni_adut(self, adut, karte):
            for karta in karte:
                nova_karta = str(karta)
                broj_karte = nova_karta[:-1]
                oznaka_karte = nova_karta[-1]
                if oznaka_karte == adut and broj_karte == 'J':
                    return karta
                elif oznaka_karte == adut and broj_karte == '9':
                    return karta
            return None

        def baci_najjacu_kartu_koja_nije_adut(self, adut, karte):
            for karta in karte:
                nova_karta = str(karta)
                broj = nova_karta[:-1]
                oznaka = nova_karta[-1]
                if oznaka != adut and broj == 'A':
                    return karta
            return None

        def baci_bilo_koju_kartu_koja_nije_adut(self, adut, karte):
            poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
            for vrijednost in poredak_vrijednosti:
                for karta in karte:
                    broj_karte = str(karta)[:-1]
                    oznaka_karte = str(karta)[-1]
                    if oznaka_karte != adut and broj_karte == vrijednost:
                        return karta
            else: #u slučaju da igrač ima sve karte u adut, neka baci najslabiji
                poredak_vrijednosti=('7', '8', 'Q', 'K', '10', 'A', '9', 'J')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if oznaka_karte == adut and broj_karte == vrijednost:
                            return karta

        def provjeri_prethodno_bacenu_kartu(self, adut, karte):
            broj = str(self.agent.prva_karta)[:-1]
            oznaka = str(self.agent.prva_karta)[-1]
            bacena_devetka_adut = False
            bacen_donjak_adut = False
            mora_bacit_adut = False
            bacen_adut = False

            if oznaka == adut:
                bacen_adut = True

            if broj == '9' and oznaka == adut:
                bacena_devetka_adut = True
            elif broj == 'J' and oznaka == adut:
                bacen_donjak_adut = True

            '''
            Bačen je adut, provjerava se koja karta zbog hijerarhije,
            ako osoba nema aduta, onda se baca bilo koja druga karta
            '''

            if bacen_adut:
                poredak_vrijednosti=['J', '9', 'A', '10', 'K', 'Q', '8', '7']
                if bacen_donjak_adut:
                    poredak_vrijednosti=['7', '8', 'Q', 'K', '10', 'A', '9']
                elif bacena_devetka_adut:
                    poredak_vrijednosti=['J', '7', '8', 'Q', 'K', '10', 'A']
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if oznaka_karte == adut and broj_karte == vrijednost:
                            return karta
                else:
                    poredak_vrijednosti=['7', '8', '9', 'J', 'Q', 'K', '10', 'A']
                    karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                    return karta
            elif not bacen_adut:
                if broj != 'A':
                    poredak_vrijednosti =  ['A', '10', 'K', 'Q', 'J', '9', '8', '7']
                else:
                    poredak_vrijednosti=['7', '8', '9', 'J', 'Q', 'K', '10']
                for poredak in poredak_vrijednosti:
                    for karta in karte:
                        oznaka_karte = str(karta)[-1]
                        broj_karte = str(karta)[:-1]
                        if oznaka_karte == oznaka and broj_karte == poredak:
                            return karta
                else:
                    mora_bacit_adut = True
            if mora_bacit_adut:
                poredak_vrijednosti = ('7', '8', 'Q', 'K', '10', 'A', '9', 'J')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if oznaka_karte == adut and broj_karte == vrijednost:
                            return karta
                else:
                    poredak_vrijednosti=['7', '8', '9', 'J', 'Q', 'K', '10', 'A']
                    karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                    return karta

        def baci_bilo_koju_kartu(self, karte, poredak_vrijednosti):
            for vrijednost in poredak_vrijednosti:
                for karta in karte:
                    if str(karta)[:-1] == vrijednost:
                        return karta

        def provjeri_prethodno_bacene_karte(self, adut, karte):
            prva_karta = self.agent.prva_karta
            druga_karta = self.agent.druga_karta

            broj_prve_karte = str(prva_karta)[:-1]
            oznaka_prve_karte = str(prva_karta)[-1]

            broj_druge_karte = str(druga_karta)[:-1]
            oznaka_druge_karte = str(druga_karta)[-1]

            if oznaka_prve_karte == adut and oznaka_druge_karte == adut:
                if broj_prve_karte == 'J':
                    poredak_vrijednosti = ('A', '10', 'K', 'Q', '9', '7', '8')
                elif broj_druge_karte == 'J':
                    poredak_vrijednosti = ('7', '8', 'Q', 'K', '10', 'A', '9')
                else:
                    poredak_vrijednosti = ('J', '9','A', '10', 'K', 'Q', '8', '7')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if oznaka_karte == adut and broj_karte == vrijednost:
                            return karta
                else:
                    karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                    return karta

            elif oznaka_prve_karte == adut and oznaka_druge_karte != adut:
                poredak_vrijednosti=('J', '9', 'A', '10', 'K', 'Q', '8', '7')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if oznaka_karte == adut and broj_karte == vrijednost:
                                return karta
                else: #ovo je ako nema aduta
                    poredak_vrijednosti=('A', '10', 'K', 'Q', 'J', '9', '8', '7')
                    karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                    return karta

            elif oznaka_druge_karte != adut and oznaka_prve_karte != adut:
                if broj_druge_karte == 'A':
                    poredak_vrijednosti = ('7', '8', '9', 'J', 'Q', 'K', '10')
                else:
                    poredak_vrijednosti=('A', '10', 'K', 'Q', 'J', '9', '8', '7')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == oznaka_prve_karte:
                            return karta
                else: #ako nema karta pa baca adut
                    poredak_vrijednosti=('7', '8', 'Q', 'K', '10', 'A', '9', 'J')
                    for vrijednost in poredak_vrijednosti:
                        for karta in karte:
                            broj_karte = str(karta)[:-1]
                            oznaka_karte = str(karta)[-1]
                            if broj_karte == vrijednost and oznaka_karte == adut:
                                return karta
                    else: #ako nema ni adut, baca bilo što najslabije
                        poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                        karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                        return karta

            elif oznaka_prve_karte != adut and oznaka_druge_karte == adut:
                poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == oznaka_prve_karte:
                                return karta
                else:
                    poredak_vrijednosti=('7', '8', 'Q', 'K', '10', 'A', '9', 'J')
                    for vrijednost in poredak_vrijednosti:
                        for karta in karte:
                            broj_karte = str(karta)[:-1]
                            oznaka_karte = str(karta)[-1]
                            if broj_karte == vrijednost and oznaka_karte == adut:
                                return karta
                    else: #ako nema ni adut, baca bilo što najslabije
                        poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                        karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                        return karta

        def baci_zadnju_kartu(self, adut, karte):
            prva_karta = self.agent.prva_karta
            druga_karta = self.agent.druga_karta
            treca_karta = self.agent.treca_karta

            broj_prve_karte = str(prva_karta)[:-1]
            oznaka_prve_karte = str(prva_karta)[-1]

            broj_druge_karte = str(druga_karta)[:-1]
            oznaka_druge_karte = str(druga_karta)[-1]

            broj_trece_karte = str(treca_karta)[:-1]
            oznaka_trece_karte = str(treca_karta)[-1]


            if oznaka_prve_karte == adut and oznaka_druge_karte == adut and oznaka_trece_karte == adut:
                if broj_prve_karte == 'J' or broj_trece_karte == 'J':
                    poredak_vrijednosti=['7', '8', '9', 'J', 'Q', 'K', '10', 'A']
                else:
                    poredak_vrijednosti = ['J', '9','A', '10', 'K', 'Q', '8', '7']
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if oznaka_karte == adut and broj_karte == vrijednost:
                            return karta
                else:
                    if broj_druge_karte == 'J' or (broj_druge_karte == '9' and broj_prve_karte != 'J' and broj_trece_karte != 'J'):
                        poredak_vrijednosti = ['A', '10', 'K', 'Q', 'J', '9', '8', '7']
                    else:
                        poredak_vrijednosti=['7', '8', '9', 'J', 'Q', 'K', '10', 'A']
                    karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                    return karta
            elif oznaka_prve_karte != adut and oznaka_druge_karte != adut and oznaka_trece_karte != adut:
                poredak_vrijednosti=['A', '10', 'K', 'Q', 'J', '9', '8', '7']
                if broj_prve_karte == 'A' or broj_trece_karte == 'A':
                    poredak_vrijednosti=['7', '8', '9', 'J', 'Q', 'K', '10', 'A']
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == oznaka_prve_karte:
                            return karta
                else: #ako nema karta pa baca adut
                    poredak_vrijednosti=('7', '8', 'Q', 'K', '10', 'A', '9', 'J')
                    for vrijednost in poredak_vrijednosti:
                        for karta in karte:
                            broj_karte = str(karta)[:-1]
                            oznaka_karte = str(karta)[-1]
                            if broj_karte == vrijednost and oznaka_karte == adut:
                                return karta
                    else:
                        if broj_druge_karte == 'A':
                            poredak_vrijednosti=('A', '10', 'K', 'Q', 'J', '9', '8', '7')
                        else:
                             poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', '11')
                        karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                        return karta
            elif oznaka_prve_karte != adut and oznaka_druge_karte == adut and oznaka_trece_karte != adut:
                poredak_vrijednosti=('A', '10', 'K', 'Q', 'J', '9', '8', '7')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == oznaka_prve_karte:
                            return karta
                else: #baca adut
                    poredak_vrijednosti=('9', 'A', '10', 'K', 'Q', '8', '7', 'J')
                    for vrijednost in poredak_vrijednosti:
                        for karta in karte:
                            broj_karte = str(karta)[:-1]
                            oznaka_karte = str(karta)[-1]
                            if broj_karte == vrijednost and oznaka_karte == adut:
                                return karta
                    else: #ako nema ni adut, baca bilo što najjače jer njegov tim kupi
                        poredak_vrijednosti=('A', '10', 'K', 'Q', 'J', '9', '8', '7')
                        karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                        return karta
            elif oznaka_prve_karte != adut and oznaka_druge_karte != adut and oznaka_trece_karte == adut:
                poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == oznaka_prve_karte:
                            return karta
                else: #baca adut
                    poredak_vrijednosti=('J', '9', 'A', '10', 'K', 'Q', '8', '7')
                    for vrijednost in poredak_vrijednosti:
                        for karta in karte:
                            broj_karte = str(karta)[:-1]
                            oznaka_karte = str(karta)[-1]
                            if broj_karte == vrijednost and oznaka_karte == adut:
                                return karta
                    else: #ako nema ni adut, baca bilo što najslabije jer njegov tim ne kupi
                        poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                        karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                        return karta
            elif oznaka_prve_karte == adut and oznaka_druge_karte != adut and oznaka_trece_karte == adut:
                if broj_prve_karte == 'J' or broj_trece_karte == 'J':
                    poredak_vrijednosti=('7', '8', 'Q', 'K', '10', 'A', '9')
                else:
                    poredak_vrijednosti=('J', '9', 'A', '10', 'K', 'Q', '8', '7')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == adut:
                            return karta
                else: #ako nema ni adut, baca bilo što najslabije jer njegov tim ne kupi
                    poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                    karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                    return karta
            elif oznaka_prve_karte == adut and oznaka_druge_karte == adut and oznaka_trece_karte != adut:
                if broj_druge_karte == 'J' and (broj_prve_karte == '9' or broj_trece_karte == '9'):
                    poredak_vrijednosti=('10', 'K', 'Q', 'J', '8', '7', '9', 'A')
                elif broj_prve_karte == 'J':
                    poredak_vrijednosti=('7', '8', 'Q', 'K', '10', 'A', '9')
                elif broj_druge_karte == 'J' and broj_prve_karte != '9' and broj_trece_karte != '9':
                    poredak_vrijednosti = ('A', '10', 'K', 'Q', '8', '7', '9')
                else:
                    poredak_vrijednosti=('J', '9', 'A', '10', 'K', 'Q', '8', '7')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == adut:
                            return karta
                else: #ako nema ni adut, baca bilo što najslabije jer njegov tim ne kupi
                    poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                    karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                    return karta
            else:
                poredak_vrijednosti=('A', '10', 'K', 'Q', 'J', '8', '7', '9')
                if oznaka_prve_karte == adut:
                    if broj_prve_karte != 'J':
                        poredak_vrijednosti=('J', '9', 'A', '10', 'K', 'Q', '8', '7')
                    else:
                        poredak_vrijednosti=('7', '8', 'Q', 'K', '10', 'A', '9')
                for vrijednost in poredak_vrijednosti:
                    for karta in karte:
                        broj_karte = str(karta)[:-1]
                        oznaka_karte = str(karta)[-1]
                        if broj_karte == vrijednost and oznaka_karte == oznaka_prve_karte:
                            return karta
                else:
                    poredak_vrijednosti=('J', '9', 'A', '10', 'K', 'Q', '8', '7')
                    for vrijednost in poredak_vrijednosti:
                        for karta in karte:
                            broj_karte = str(karta)[:-1]
                            oznaka_karte = str(karta)[-1]
                            if broj_karte == vrijednost and oznaka_karte == adut:
                                return karta
                    else:
                        poredak_vrijednosti=('7', '8', '9', 'J', 'Q', 'K', '10', 'A')
                        karta = self.baci_bilo_koju_kartu(karte, poredak_vrijednosti)
                        return karta

    async def setup(self):
        self.igra=False
        self.odigrao=False

        fsm = self.PonasanjeKA()

        fsm.add_state(name="Cekaj", state=self.Cekaj(), initial=True)
        fsm.add_state(name="Odigraj", state=self.Odigraj())

        fsm.add_transition(source="Cekaj", dest="Odigraj")
        fsm.add_transition(source="Odigraj", dest="Cekaj")
        fsm.add_transition(source="Cekaj", dest="Cekaj")

        self.add_behaviour(fsm)

    def dodaj_kartu(self, karta):
        self.karte.append(karta)

    def baci_kartu(self, karta):
        self.karte.remove(karta)

    def postavi_uvjete_za_rundu(self, redoslijed, adut, runda = 1, prva_karta = "", druga_karta = "", treca_karta = ""):
        self.redoslijed = redoslijed
        self.bacena_karta = ""
        self.runda = runda
        self.adut = adut
        self.prva_karta = prva_karta
        self.druga_karta = druga_karta
        self.treca_karta = treca_karta
        self.igra = True
        while(self.odigrao is False):
            time.sleep(0.1)
        self.odigrao=False
        return self.bacena_karta


class Belot:
    def __init__(self, agenti):
        self.igraci = agenti
        self.tim1 = [self.igraci[0], self.igraci[2]]
        self.tim2 = [self.igraci[1], self.igraci[3]]
        self.tim1_bodovi = 0
        self.tim2_bodovi = 0
        self.adut = None
        self.prvi_agent_za_biranje_aduta = 0 # treba provjera ako stavim 1
        self.trenutni_igrac = self.igraci[0]
        self.trenutni_stih = []

    def kreiraj_spil(self):
        brojevi = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        znakovi = ['♠', '♣', '♦', '♥']
        return [Karta(broj, znak) for broj in brojevi for znak in znakovi]

    def promijesaj_spil(self):
        random.shuffle(self.spil)

    def podijeli_karte_igracima(self):
        self.promijesaj_spil()
        for _ in range(6):
            for igrac in self.igraci:
                igrac.dodaj_kartu(self.spil.pop())

    def pokaziKarte(self):
        print('------------------------ Karte svih igrača ----------------------------')
        for igrac in self.igraci:
            print(f"Karte igraca {igrac.ime}: {igrac.karte}")

    def ima_devetku_i_decka(self, igrac):
        devetka = False
        decko = False
        znakovi = {'♠': 0, '♣': 0, '♦': 0, '♥': 0}

        for karta in igrac.karte:
            if karta.broj == '9':
                devetka = True
                znakovi[karta.znak] += 1
            if karta.broj == 'J':
                decko = True
                znakovi[karta.znak] += 1
            if devetka and decko and any(val == 2 for val in znakovi.values()):
                najvise_karata = max(znakovi.values())
                for znak, broj_karata in znakovi.items():
                    if broj_karata == najvise_karata:
                        self.adut = znak
                        break
                print(f"Adut je: {self.adut}")
                return True
        return False

    def odredi_adut(self):
        agent_za_odabir_aduta = self.prvi_agent_za_biranje_aduta
        print("----------------------- Odabir aduta --------------------------")
        agenti_koji_preskacu = []
        for _ in range(4):
            self.igraci[agent_za_odabir_aduta].zvao_adut = False
            trenutni_agent = self.igraci[agent_za_odabir_aduta]
            if self.ima_devetku_i_decka(trenutni_agent):
                self.igraci[agent_za_odabir_aduta].zvao_adut = True
                break
            else:
                agenti_koji_preskacu.append(agent_za_odabir_aduta)
                print(f'Agent {self.igraci[agent_za_odabir_aduta].ime} kaže dalje.')
                agent_za_odabir_aduta = (agent_za_odabir_aduta + 1) % 4
        else:
            print(f'Agent {self.igraci[agenti_koji_preskacu[0]].ime} je na musu i odabire adut na temelju najviše karata.')
            self.igraci[agenti_koji_preskacu[0]].zvao_adut = True
            self.odaberi_adut_na_temelju_najvise_karata(self.igraci[agenti_koji_preskacu[0]])

        self.prvi_agent_za_biranje_aduta = (self.prvi_agent_za_biranje_aduta + 1) % 4
        print(f"Prvi agent u idućoj rundi za odabir aduta bit će {self.igraci[self.prvi_agent_za_biranje_aduta].ime}")

    def odaberi_adut_na_temelju_najvise_karata(self, igrac):
        znakovi = {'♠': 0, '♣': 0, '♦': 0, '♥': 0}
        for karta in igrac.karte:
            znakovi[karta.znak] += 1

        najvise_karata = max(znakovi.values())
        for znak, broj_karata in znakovi.items():
            if broj_karata == najvise_karata:
                self.adut = znak
                break

        print(f"---- Adut je: {self.adut} ----")

    def podijeli_preostale_karte(self):
        for _ in range(2):
            for igrac in self.igraci:
                igrac.dodaj_kartu(self.spil.pop())

    def zvanje_bodovi(self, karte):
        brojac_karata = {'7': 0, '8': 0, '9': 0, '10': 0, 'J': 0, 'Q': 0, 'K': 0, 'A': 0}
        for karta in karte:
            brojac_karata[karta.broj] += 1

        zvanje = 0
        if brojac_karata['J'] == 4:
            zvanje = 200
        elif brojac_karata['9'] == 4:
            zvanje = 150
        elif brojac_karata['A'] == 4 or brojac_karata['10'] == 4 or brojac_karata['K'] == 4 or brojac_karata['Q'] == 4:
            zvanje = 100
        return zvanje

    def provjeri_zvanja(self):
        najvece_zvanje = 0
        bodovi_po_igracima = []
        for i, igrac in enumerate(self.igraci):
            pobjeda = self.provjeri_niz_karata(igrac.karte)
            if pobjeda:
                print(f"{igrac.ime} dobiva zvanje koje vrijedi 301 bod te je igra završena!")
                for igrac in self.igraci:
                    igrac.stop()
                    time.sleep(5)
                quit()
            bodovi_zvanja = self.zvanje_bodovi(igrac.karte)
            bodovi_po_igracima.append(bodovi_zvanja)
        najvece_zvanje = max(bodovi_po_igracima)
        print(f"Bodovi zvanja: {bodovi_po_igracima}")
        if najvece_zvanje != 0:
            i = bodovi_po_igracima.index(najvece_zvanje)
            tim = 1 if i % 2 == 0 else 2
            if tim == 1:
                self.bodovi_zvanja_tim1 = najvece_zvanje
            else:
                self.bodovi_zvanja_tim2 = najvece_zvanje
            print(f"Tim {tim} dobiva zvanje koje vrijedi {najvece_zvanje} bodova!")
        else:
            bodovi_po_igracima = []
            for i, igrac in enumerate(self.igraci):
                bodovi_zvanja = self.provjeri_slabija_zvanja(igrac.karte)
                bodovi_po_igracima.append(bodovi_zvanja)
            najvece_zvanje = max(bodovi_po_igracima)
            print(f"Bodovi slabijih zvanja: {bodovi_po_igracima}")
            if najvece_zvanje != 0:
                i = bodovi_po_igracima.index(najvece_zvanje)
                tim = 1 if i % 2 == 0 else 2
                if tim == 1:
                    self.bodovi_zvanja_tim1 = najvece_zvanje
                else:
                    self.bodovi_zvanja_tim2 = najvece_zvanje
                print(f"Tim {tim} dobiva zvanje koje vrijedi {najvece_zvanje} bodova!")

    def provjeri_slabija_zvanja(self, karte):
        brojevi = ["A", "K", "Q", "J", "10", "9", "8", "7"]
        znakovi = ["♠", "♣", "♦", "♥"]

        nove_karte = list(map(str, karte))

        najjace_zvanje = 0
        for znak in znakovi:
            niz = 0
            for broj in brojevi:
                karta = f"{broj}{znak}"
                if karta in nove_karte:
                    niz += 1
                else:
                    if niz == 3:
                        najjace_zvanje = max(najjace_zvanje, 20)
                    elif niz == 4:
                        najjace_zvanje = max(najjace_zvanje, 50)
                    elif niz >= 5:
                        najjace_zvanje = max(najjace_zvanje, 100)
                    niz = 0

        return najjace_zvanje

    def provjeri_niz_karata(self, karte):
        znakovi = ["♠", "♣", "♦", "♥"]

        nove_karte = list(map(str, karte))
        pobjeda = False
        for znak in znakovi:
            niz = 0
            for karta in nove_karte:
                if karta[-1] == znak:
                    niz = niz + 1
                    if niz == 8:
                        pobjeda = True
                        return pobjeda
        return pobjeda

    def dodaj_bodove(self, tim, bodovi):
        if tim == 1:
            self.tim1_bodovi += bodovi
        elif tim == 2:
            self.tim2_bodovi += bodovi

    def provjeri_pobjednika(self):
        if self.tim1_bodovi >= 301 and self.tim1_bodovi > self.tim2_bodovi:
            return 1
        elif self.tim2_bodovi >= 301:
            return 2
        else:
            return None

    def provjeri_tko_kupi(self, stih):
        poredak_vrijednosti = ('A', '10', 'K', 'Q', 'J', '9', '8', '7')
        poredak_adut = ('J', '9', 'A', '10', 'K', 'Q', '8', '7')
        boja_prve_karte = str(stih[0])[-1]
        najjaca_karta = None
        najjaca_vrijednost = None
        naden_adut = False
        for karta in stih:
            boja_karte = str(karta)[-1]
            vrijednost_karte = str(karta)[:-1]

            if boja_karte == self.adut:
                naden_adut = True

        for karta in stih:
            boja_karte = str(karta)[-1]
            vrijednost_karte = str(karta)[:-1]
            # Provjera za adute
            if boja_karte == self.adut:
                if vrijednost_karte in poredak_adut:
                    trenutna_vrijednost = poredak_adut.index(vrijednost_karte)
                    if najjaca_vrijednost is None or trenutna_vrijednost < najjaca_vrijednost:
                        najjaca_karta = karta
                        najjaca_vrijednost = trenutna_vrijednost
            # Provjera za istu boju kao prve karte
            elif boja_karte == boja_prve_karte and not naden_adut:
                if vrijednost_karte in poredak_vrijednosti:
                    trenutna_vrijednost = poredak_vrijednosti.index(vrijednost_karte)
                    if najjaca_vrijednost is None or trenutna_vrijednost < najjaca_vrijednost:
                        najjaca_karta = karta
                        najjaca_vrijednost = trenutna_vrijednost
        return najjaca_karta

    def provjeri_bodove(self, tim, adut):
        bodovi = 0
        bodovi_adut = {'A': 11, '10': 10, 'K': 4, 'Q': 3, 'J': 20, '9': 14, '8': 0, '7': 0}
        bodovi_neadut = {'A': 11, '10': 10, 'K': 4, 'Q': 3, 'J': 2, '9': 0, '8': 0, '7': 0}
        for karta in tim:
            vrijednost, boja = str(karta)[:-1], str(karta)[-1]

            if boja == adut:
                bodovi += bodovi_adut[vrijednost]
            else:
                bodovi += bodovi_neadut[vrijednost]
        return bodovi

    def provjeri_zvanje_bele(self):
        for i, igrac in enumerate(self.igraci):
            ima_damu = False
            ima_kralja = False
            for karta in igrac.karte:
                oznaka_karte = str(karta)[-1]
                broj_karte = str(karta)[:-1]
                if oznaka_karte == self.adut and broj_karte == 'K':
                    ima_kralja = True
                elif oznaka_karte == self.adut and broj_karte == 'Q':
                    ima_damu = True
            if ima_damu and ima_kralja:
                igrac.ima_zvanje_bele = True
                tim = 1 if i % 2 == 0 else 2
                if tim == 1:
                    self.bodovi_zvanja_tim1 += 20
                else:
                    self.bodovi_zvanja_tim2 += 20
                print(f"{igrac.ime} ima zvanje Bele")

    def igraj(self):
        kraj = False

        while(not kraj):
            self.bodovi_zvanja_tim1 = 0
            self.bodovi_zvanja_tim2 = 0
            self.spil = self.kreiraj_spil()
            self.podijeli_karte_igracima()
            self.pokaziKarte()
            self.odredi_adut()
            self.podijeli_preostale_karte()
            self.pokaziKarte()
            self.provjeri_zvanja()
            self.trenutni_stih_i_igrac = []
            self.karte_tima_1 = []
            self.karte_tima_2 = []
            self.trenutni_igrac = self.igraci[self.prvi_agent_za_biranje_aduta]
            self.provjeri_zvanje_bele()
            igrac = self.prvi_agent_za_biranje_aduta
            runda = 1
            redoslijed = 1
            karta = None

            while(runda <= 8):
                karta=self.trenutni_igrac.postavi_uvjete_za_rundu(redoslijed, self.adut, runda)
                prva_karta=karta
                self.trenutni_stih.append(karta)
                self.trenutni_stih_i_igrac.append(self.trenutni_igrac.ime)
                self.trenutni_stih_i_igrac.append(karta)
                redoslijed+= 1
                time.sleep(0.1)

                self.trenutni_igrac = self.igraci[(igrac + 1) % 4]
                karta=self.trenutni_igrac.postavi_uvjete_za_rundu(redoslijed, self.adut, runda, prva_karta)
                druga_karta=karta
                self.trenutni_stih.append(karta)
                self.trenutni_stih_i_igrac.append(self.trenutni_igrac.ime)
                self.trenutni_stih_i_igrac.append(karta)
                redoslijed+=1
                time.sleep(0.1)

                self.trenutni_igrac = self.igraci[(igrac + 2) % 4]
                karta=self.trenutni_igrac.postavi_uvjete_za_rundu(redoslijed, self.adut, runda, prva_karta, druga_karta)
                treca_karta=karta
                self.trenutni_stih.append(karta)
                self.trenutni_stih_i_igrac.append(self.trenutni_igrac.ime)
                self.trenutni_stih_i_igrac.append(karta)
                redoslijed+=1
                time.sleep(0.1)

                self.trenutni_igrac = self.igraci[(igrac + 3) % 4]
                karta=self.trenutni_igrac.postavi_uvjete_za_rundu(redoslijed, self.adut, runda, prva_karta, druga_karta, treca_karta)
                self.trenutni_stih.append(karta)
                self.trenutni_stih_i_igrac.append(self.trenutni_igrac.ime)
                self.trenutni_stih_i_igrac.append(karta)
                time.sleep(0.1)

                najjaca_karta = self.provjeri_tko_kupi(self.trenutni_stih)
                print(f"Najjača bačena karta je: {najjaca_karta}")

                indeks = self.trenutni_stih_i_igrac.index(najjaca_karta)
                igrac = self.trenutni_stih_i_igrac[indeks-1]

                if igrac == 'Igrac 1':
                    igrac = 0
                elif igrac == 'Igrac 2':
                    igrac = 1
                elif igrac == 'Igrac 3':
                    igrac = 2
                elif igrac == 'Igrac 4':
                    igrac = 3

                self.trenutni_igrac = self.igraci[igrac]

                if igrac == 0 or igrac == 2:
                    self.karte_tima_1 = self.karte_tima_1 + self.trenutni_stih
                else:
                    self.karte_tima_2 = self.karte_tima_2 + self.trenutni_stih

                print(f"Bačene karte su: {self.trenutni_stih} i kupi ih {self.trenutni_igrac.ime}")
                print("------------------------ Karte po timovima ----------------------------")
                print(f"Karte prvog tima: {self.karte_tima_1}")
                print(f"Karte drugog tima: {self.karte_tima_2}")

                self.trenutni_stih = []
                self.trenutni_stih_i_igrac = []

                if runda < 8:
                    print(f'----------------------------- Karte igrača nakon {runda}. bacanja ------------------------------')
                    for novo_stanje in self.igraci:
                        print(f"Karte igrača {novo_stanje.ime}: {novo_stanje.karte}")
                    print('--------------------------------------------------------------------------------------------')

                runda += 1
                redoslijed = 1
            #dodjela bodova nakon svake runde
            bodovi_1 = self.provjeri_bodove(self.karte_tima_1, self.adut)
            bodovi_2 = self.provjeri_bodove(self.karte_tima_2, self.adut)

            if bodovi_1 == 0:
                bodovi_2 += 90
            if bodovi_2 == 0:
                bodovi_1 += 90

            if igrac == 0 or igrac == 2:
                bodovi_1 += 10
            else:
                bodovi_2 += 10

            print("---------------------- Bodovi timova prije provjere pada ------------------------")
            print(f"Tim 1 ima: {bodovi_1} bodova")
            print(f"Tim 2 ima: {bodovi_2} bodova")
            print("---------------------------------------------------------------------------------")

            igrac_zvao_adut = 0

            for i, igrac_zvao in enumerate(self.igraci):
                if igrac_zvao.zvao_adut == True:
                    igrac_zvao_adut = i
                    break

            ukupni_bodovi = bodovi_1 + bodovi_2 + self.bodovi_zvanja_tim1 + self.bodovi_zvanja_tim2
            bodovi_za_prolaz = (ukupni_bodovi / 2) +1

            if igrac_zvao_adut == 0 or igrac_zvao_adut == 2:
                if bodovi_1 < bodovi_za_prolaz:
                    bodovi_2 += bodovi_1
                    bodovi_1 = 0
                    self.bodovi_zvanja_tim2 = self.bodovi_zvanja_tim1
                    self.bodovi_zvanja_tim1 = 0
            if igrac_zvao_adut == 1 or igrac_zvao_adut == 3:
                if bodovi_2 < bodovi_za_prolaz:
                    bodovi_1 += bodovi_2
                    bodovi_2 = 0
                    self.bodovi_zvanja_tim1 = self.bodovi_zvanja_tim2
                    self.bodovi_zvanja_tim2 = 0

            self.dodaj_bodove(1, bodovi_1 + self.bodovi_zvanja_tim1)
            self.dodaj_bodove(2, bodovi_2 + self.bodovi_zvanja_tim2)

            print("---------------------- Bodovi timova ------------------------")
            print(f"Tim 1 ima: {self.tim1_bodovi} bodova")
            print(f"Tim 2 ima: {self.tim2_bodovi} bodova")
            print("-------------------------------------------------------------")

            pobjednik = self.provjeri_pobjednika()
            if pobjednik:
                print(f"Tim {pobjednik} je pobijedio s {self.tim1_bodovi if pobjednik == 1 else self.tim2_bodovi} bodova!")
                kraj = True

        for igrac in self.igraci:
            igrac.stop()

        quit_spade()


def postavi():
    parser = ArgumentParser()
    parser.add_argument(
        "-jid1", type=str, help="JID 1. agenta", default="agent@rec.foi.hr")
    parser.add_argument(
        "-pwd1", type=str, help="Lozinka 1. agenta", default="tajna")
    parser.add_argument(
        "-ime1", type=str, help="Ime 1. agenta", default="Igrac 1")
    parser.add_argument(
        "-jid2", type=str, help="JID 2. agenta", default="primatelj@rec.foi.hr")
    parser.add_argument(
        "-pwd2", type=str, help="Lozinka 2. agenta", default="tajna")
    parser.add_argument(
        "-ime2", type=str, help="Ime 2. agenta", default="Igrac 2")
    parser.add_argument(
        "-jid3", type=str, help="JID 3. agenta", default="barbara@rec.foi.hr")
    parser.add_argument(
        "-pwd3", type=str, help="Lozinka 3. agenta", default="barbara")
    parser.add_argument(
        "-ime3", type=str, help="Ime 3. agenta", default="Igrac 3")
    parser.add_argument(
        "-jid4", type=str, help="JID 4. agenta", default="posiljatelj@rec.foi.hr")
    parser.add_argument(
        "-pwd4", type=str, help="Lozinka 4. agenta", default="tajna")
    parser.add_argument(
        "-ime4", type=str, help="Ime 4. agenta", default="Igrac 4")
    args = parser.parse_args()

    igrac1 = Igrac(args.jid1, args.pwd1, args.ime1)
    igrac1.start()

    igrac2 = Igrac(args.jid2, args.pwd2, args.ime2)
    igrac2.start()

    igrac3 = Igrac(args.jid3, args.pwd3, args.ime3)
    igrac3.start()

    igrac4 = Igrac(args.jid4, args.pwd4, args.ime4)
    igrac4.start()

    agenti = [igrac1, igrac2, igrac3, igrac4]

    time.sleep(45)

    return agenti

if __name__ == "__main__":

    agenti = postavi()
    belot = Belot(agenti)
    belot.igraj()