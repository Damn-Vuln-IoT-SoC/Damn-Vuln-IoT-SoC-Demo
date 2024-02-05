from migen import *
from litex.soc.interconnect.csr import *

class Counter(Module, AutoCSR):
    def __init__(self, width=32, init=0):
        self.width = width

        # Créer le registre de contrôle pour démarrer et arrêter le compteur
        self.start = CSRStorage(name="control")

        # Créer le registre de contrôle pour lire la valeur du compteur
        self.value = CSRStatus(width, name="value")

        # Créer le registre pour stocker la valeur du compteur
        self.count = Signal(width, reset=init)

        # Ajouter ici la logique pour incrémenter le compteur à chaque cycle
        running = Signal()
        self.sync += If(running, self.count.eq(self.count + 1))
        
        # Démarrer ou arrêter le compteur en fonction des registres de contrôle
        self.sync += If(self.start.storage == 1, running.eq(1))
        self.sync += If(self.start.storage == 0, running.eq(0))

        # Mettre à jour la valeur du registre de contrôle avec la valeur actuelle du compteur
        self.comb += self.value.status.eq(self.count)