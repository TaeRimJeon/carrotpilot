"""Boot-latched DM configuration; the retired DisableDM never disables monitoring."""
import os


def monitoring_mode(params):
  try:
    return int(os.environ.get("CARROT_DM_MODE", str(params.get_int("DriverMonitoringMode"))))
  except ValueError:
    return 0


def experimental_mode(params):
  return monitoring_mode(params) == 1


def drowsy_only_mode(params):
  return monitoring_mode(params) == 2


def configure_monitoring(params, environ=None):
  env = os.environ if environ is None else environ
  # Old mode 2 also enabled road streaming. Preserve only that independent feature.
  if params.get("DriverMonitoringMode") is None:
    if params.get("CarrotVisionEnabled") is None:
      params.put_bool("CarrotVisionEnabled", params.get_int("DisableDM") == 2)
    params.put_int("DriverMonitoringMode", 0)
  mode = params.get_int("DriverMonitoringMode")
  env["CARROT_DM_MODE"] = str(mode if mode in (0, 1, 2) else 0)
