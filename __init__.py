# -*- coding: utf-8 -*-
################################################################################

from modules import cbpi
from modules.core.controller import FermenterController
from modules.core.props import Property

################################################################################
@cbpi.fermentation_controller
class HardTarget(FermenterController):

    heater_offset_min = Property.Number("Heater Offset ON", True, 0, description="Offset as decimal number when the heater is switched on. Should be greater then 'Heater Offset OFF'. For example a value of 2 switches on the heater if the current temperature is 2 degrees below the target temperature")
    heater_offset_max = Property.Number("Heater Offset OFF", True, 0, description="Offset as decimal number when the heater is switched off. Should be smaller then 'Heater Offset ON'. For example a value of 1 switches off the heater if the current temperature is 1 degree below the target temperature")
    cooler_offset_min = Property.Number("Cooler Offset ON", True, 0, description="Offset as decimal number when the cooler is switched on. Should be greater then 'Cooler Offset OFF'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees above the target temperature")
    cooler_offset_max = Property.Number("Cooler Offset OFF", True, 0, description="Offset as decimal number when the cooler is switched off. Should be less then 'Cooler Offset ON'. For example a value of 1 switches off the cooler if the current temperature is 1 degree above the target temperature")

    hard_target_temp  = Property.Number("Hard Target", True, description="Hard target temperature to prevent accidental changes.")

    #-------------------------------------------------------------------------------
    def stop(self):
        super(FermenterController, self).stop()

        self.heater_off()
        self.cooler_off()

    #-------------------------------------------------------------------------------
    def run(self):
        while self.is_running():

            target_temp = self.get_target_temp()
            temp = self.get_temp()

            if temp + float(self.heater_offset_min) <= target_temp:
                self.heater_on(100)

            if temp + float(self.heater_offset_max) >= target_temp:
                self.heater_off()

            if temp >= target_temp + float(self.cooler_offset_min):
                self.cooler_on(100)

            if temp <= target_temp + float(self.cooler_offset_max):
                self.cooler_off()

            self.sleep(1)

################################################################################
@cbpi.backgroundtask(key="hard_target_update", interval=5)
def hard_target_update(api):
    for key, fermenter in cbpi.cache.get("fermenter").iteritems():
        if fermenter.logic == "HardTarget":

            # restart controller if stopped
            if fermenter.state is False:
                cbpi.notify("Restarting Auto Mode", str(fermenter.name), timeout=5000)
                cbpi.app.logger.info("hard_target_update: restarting auto mode for '{}'".format(fermenter.name))
                cfg = fermenter.config.copy()
                cfg.update(dict(api=cbpi, fermenter_id=fermenter.id, heater=fermenter.heater, sensor=fermenter.sensor))
                instance = cbpi.get_fermentation_controller(fermenter.logic).get("class")(**cfg)
                instance.init()
                fermenter.instance = instance
                def run(instance):
                    instance.run()
                t = cbpi.socketio.start_background_task(target=run, instance=instance)
                fermenter.state = True
                cbpi.emit("UPDATE_FERMENTER", cbpi.cache.get("fermenter")[key])

            # reset target temp if changed
            hard_target = float(fermenter.config['hard_target_temp'])
            if float(fermenter.target_temp) != hard_target:
                cbpi.notify("Resetting Target Temp", str(fermenter.name), timeout=5000)
                cbpi.app.logger.info("hard_target_update: resetting taget temp for '{}'".format(fermenter.name))
                cbpi.cache.get("fermenter")[key].target_temp = hard_target
                cbpi.emit("UPDATE_FERMENTER_TARGET_TEMP", {"id": key, "target_temp": hard_target})
