from openpilot.common.realtime import DT_CTRL
from openpilot.common.params import Params

class CarrotControls:
  def __init__(self, CP):
    self.CP = CP
    self.params = Params()
    self.lat_suspend_active = False
    self.lat_suspend_enter_t = 0.0
    self.lat_suspend_hold_t = 0.0

  def lat_suspend_control(self, CS, latActive):
    suspend_angle = float(self.params.get_int("LatSuspendAngleDeg"))
    blinker_speed_kph = self.params.get_int("BlinkerLateralSuspendSpeed")
    resume_angle  = 15
    delay_sec     = 1.0
    hold_sec      = 0.5

    # Low-speed turn signal temporarily suspends lateral control.
    # vEgo is m/s, setting is km/h. 0 disables this feature.
    blinker_suspend = (
      blinker_speed_kph > 0
      and CS.vEgo <= blinker_speed_kph / 3.6
      and (CS.leftBlinker or CS.rightBlinker)
    )

    # 1) enter condition timer
    enter_cond = CS.steeringPressed and abs(CS.steeringAngleDeg) > suspend_angle
    if not self.lat_suspend_active:
      if enter_cond:
        self.lat_suspend_enter_t += DT_CTRL
        if self.lat_suspend_enter_t >= delay_sec:
          self.lat_suspend_active = True
          self.lat_suspend_hold_t = 0.0
      else:
        self.lat_suspend_enter_t = 0.0

    # 2) while suspended: enforce minimum hold time + hysteresis exit
    if self.lat_suspend_active:
      self.lat_suspend_hold_t += DT_CTRL

      exit_cond = (abs(CS.steeringAngleDeg) < resume_angle) and (not CS.steeringPressed)
      if (self.lat_suspend_hold_t >= hold_sec) and exit_cond:
        self.lat_suspend_active = False
        self.lat_suspend_enter_t = 0.0

    if self.lat_suspend_active or blinker_suspend:
      latActive = False
    return latActive