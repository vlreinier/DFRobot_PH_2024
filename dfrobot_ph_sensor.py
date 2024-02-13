
import os.path
import json


class DFRobotPHSensor:
    DEFAULT_NEUTRAL_VOLTAGE = 1500.0
    DEFAULT_ACID_VOLTAGE = 2032.44

    def __init__(
        self, calibration_json_path: str = "ph_calibration_data.json", makedirs: bool = True
    ) -> None:
        self.calibration_json_path = calibration_json_path
        self.neutral_voltage = self.DEFAULT_NEUTRAL_VOLTAGE
        self.acid_voltage = self.DEFAULT_ACID_VOLTAGE
        self.makedirs = makedirs
        self._initialize_calibration_data()
        self.print_active_voltages()

    def print_active_voltages(self):
        print(f"Active neutral voltage for PH 7:    {self.neutral_voltage} mV")
        print(f"Active acid voltage for PH 4:       {self.acid_voltage} mV")

    def _initialize_calibration_data(self) -> None:
        if not os.path.isfile(self.calibration_json_path):
            self._store_calibration_data()
        else:
            self._load_calibration_data()

    def _load_calibration_data(self) -> None:
        print(f"Loading calibration data from {self.calibration_json_path}...")
        with open(self.calibration_json_path, "r") as f:
            calibration_data = json.load(f)
            self.neutral_voltage = calibration_data["neutral_voltage"]
            self.acid_voltage = calibration_data["acid_voltage"]
            self._verify_voltages()

    def _verify_voltages(self) -> None:
        if not self.is_valid_ph7_voltage(self.neutral_voltage):
            raise ValueError(f"The mV value {self.neutral_voltage} for neutral PH 7 is not valid.")
        if not self.is_valid_ph4_voltage(self.acid_voltage):
            raise ValueError(f"The mV value {self.acid_voltage} for acid PH 4 is not valid.")

    def _store_calibration_data(self) -> None:
        print(f"Storing calibration data in {self.calibration_json_path}...")
        self._verify_voltages()
        calibration_data = {
            "neutral_voltage": self.neutral_voltage,
            "acid_voltage": self.acid_voltage,
        }
        folder = os.path.dirname(os.path.abspath(self.calibration_json_path))
        if folder and not os.path.exists(folder):
            if self.makedirs:
                os.makedirs(folder)
            else:
                raise FileNotFoundError(
                    f"The directory {folder} does not exist. "
                    "Use makedirs=True to create the folder automatically."
                )
        with open(self.calibration_json_path, "w") as f:
            json.dump(calibration_data, f)

    def _calculate_ph(self, mv: float) -> float:
        slope = (7.0 - 4.0) / (
            (self.neutral_voltage - 1500.0) / 3.0 - (self.acid_voltage - 1500.0) / 3.0
        )
        intercept = 7.0 - slope * (self.neutral_voltage - 1500.0) / 3.0
        ph_value = slope * (mv - 1500.0) / 3.0 + intercept
        return ph_value

    def read_ph(self, mv: float, round_to: int = 2) -> float:
        ph_value = round(self._calculate_ph(mv), round_to)
        return ph_value

    def read_ph_temp_compensation(
        self, mv: float, temperature: float, coefficient: float = 0.01, round_to: int = 2
    ) -> float:
        compensation_coefficient = 1.0 + coefficient * (temperature - 25.0)
        compensation_voltage = mv / compensation_coefficient
        compensated_ph_value = round(self._calculate_ph(compensation_voltage), round_to)
        return compensated_ph_value

    @staticmethod
    def is_valid_ph7_voltage(mv: float) -> bool:
        return mv and 1322 < mv < 1678

    @staticmethod
    def is_valid_ph4_voltage(mv: float) -> bool:
        return mv and 1854 < mv < 2210

    def auto_calibrate(self, mv: float) -> None:
        if self.is_valid_ph7_voltage(mv):
            self.calibrate_ph7(mv)
        elif self.is_valid_ph4_voltage(mv):
            self.calibrate_ph4(mv)
        else:
            raise ValueError(
                f"Auto calibration does not work for {mv} mV."
                f"Use a designated calibration method."
            )

    def calibrate_ph7(self, mv: float) -> None:
        self.neutral_voltage = mv
        self._store_calibration_data()
        print(f"Successfully calibrated PH7 voltage to {mv} mV")

    def calibrate_ph4(self, mv: float) -> None:
        self.acid_voltage = mv
        self._store_calibration_data()
        print(f"Successfully calibrated PH4 voltage to {mv} mV")

    def reset_to_default(self) -> None:
        self.neutral_voltage = self.DEFAULT_NEUTRAL_VOLTAGE
        self.acid_voltage = self.DEFAULT_ACID_VOLTAGE
        self._store_calibration_data()
        self.print_active_voltages()

    def set_calibration_data(self, neutral_voltage: float, acid_voltage: float) -> None:
        self.neutral_voltage = neutral_voltage
        self.acid_voltage = acid_voltage
        self._store_calibration_data()
        self.print_active_voltages()


if __name__ == "__main__":

    # Read the sensor
    ph_sensor = DFRobotPHSensor()
    print(ph_sensor.read_ph(mv=1515))
    
    # Calibrate the sensor
    ph_sensor.auto_calibrate(mv=1515)

