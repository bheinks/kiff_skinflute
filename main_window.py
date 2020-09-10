import json

# Third party imports
from PyQt5.QtWidgets import (QMainWindow)

# Local imports
from main_window_init import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Basic pyqt init for gui window
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.configuration = json.load(open("configuration.json", "r"))

        # Class variables to hold state of check boxes
        self.two_handed_enabled = True
        self.weapon_song_enabled = False
        self.haste_enabled = False
        self.power_attack_enabled = False

        # Connections to toggle state on check box click
        self.ui.two_handed_check_box.clicked.connect(self.two_handed_toggled)
        self.ui.inspire_courage_check_box.clicked.connect(self.inspire_courage_toggled)
        self.ui.haste_check_box.clicked.connect(self.haste_toggled)
        self.ui.power_attack_check_box.clicked.connect(self.power_attack_toggled)

        # Auto update when spin box toggled
        self.ui.num_hits_spin_box.valueChanged.connect(self.update_output)

        # Initialize output with initial settings
        self.update_output()

    def two_handed_toggled(self, state):
        self.two_handed_enabled = state
        self.update_output()

    def inspire_courage_toggled(self, state):
        self.weapon_song_enabled = state
        self.update_output()

    def haste_toggled(self, state):
        self.haste_enabled = state
        self.update_output()

    def power_attack_toggled(self, state):
        self.power_attack_enabled = state
        self.update_output()

    def update_output(self):
        # Calculate strength bonus
        strength = self.configuration['STR']

        effective_strength_bonus = int((strength - 10) / 2)

        # Calculate number of attacks
        num_attacks = 1 + int((self.configuration['BAB'] - 1) / 5)

        # Calculate atack bonus
        attack_bonus = self.calculate_attack_bonus(effective_strength_bonus)

        attack_text = f' Attack Bonus: +{attack_bonus}'
        if self.haste_enabled:
            attack_text = attack_text + f'/{attack_bonus}'
        for i in range(num_attacks - 1):
            attack_text = attack_text + f'/{attack_bonus - (5 * (i + 1))}'
        self.ui.attack_bonus_label.setText(attack_text)

        # Set new spin box max
        spin_max = num_attacks
        if self.haste_enabled:
            spin_max += 1
        self.ui.num_hits_spin_box.setMaximum(spin_max)

        # Get num hits
        num_hits = int(self.ui.num_hits_spin_box.value())

        # Calculate damage
        damage = self.calculate_damage(effective_strength_bonus)
        damage *= num_hits

        die = self.configuration["DAMAGE_DIE"]

        self.ui.damage_label.setText(f'Damage: {num_hits * die[0]}d{die[1]} + {damage}')

        crit_mod = self.configuration["WEAPON_CRITICAL_MOD"]
        self.ui.crit_damage_label.setText(
            f'Critical Damage: {num_hits * crit_mod * die[0]}d{die[1]} + {crit_mod * damage}')

    def calculate_attack_bonus(self, effective_strength_bonus):
        # TODO: don't hard code weapon focus
        attack_bonus = self.configuration['BAB'] + self.configuration['WEAPON_BONUS'] + effective_strength_bonus + 1

        if self.weapon_song_enabled:
            attack_bonus += self.configuration['INSPIRE']

        if self.haste_enabled:
            attack_bonus += self.configuration['HASTE']

        if self.power_attack_enabled:
            attack_bonus += self.configuration['POWER_ATTACK_ATTACK']

        return attack_bonus

    def calculate_damage(self, effective_strength_bonus):
        damage = self.configuration['WEAPON_BONUS']

        strength_damage = effective_strength_bonus
        if self.two_handed_enabled:
            strength_damage = int(strength_damage * self.configuration['TWO_HANDED_MULTI'])
        damage += strength_damage

        power_attack_damage = 6
        if self.two_handed_enabled:
            power_attack_damage = int(power_attack_damage * self.configuration['TWO_HANDED_MULTI'])
        if self.power_attack_enabled:
            damage += power_attack_damage

        if self.weapon_song_enabled:
            damage += self.configuration['INSPIRE']

        return damage
