from app.services.db_interface import DBInterface, logger
import json


class DeviceMixin:
    def unbind_device(self: DBInterface, api_key: str, device_id: str) -> bool:
        """解绑特定设备"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT bound_devices FROM api_keys WHERE key_string = ?", (api_key,)
            )
            row = cursor.fetchone()
            if not row:
                logger.warning("未找到匹配的apikey，解绑请求失败")
                return False
            devices = json.loads(row[0])
            if device_id in devices:
                devices.remove(device_id)
            else:
                logger.warning("未找到匹配的device，解绑请求失败")
                return False
            new_devices_json = json.dumps(devices)
            cursor.execute(
                "UPDATE api_keys SET bound_devices = ? WHERE key_string = ?",
                (new_devices_json, api_key),
            )
            conn.commit()
            logger.info(f"设备'{device_id[:8]}...'与apikey'{api_key[:8]}...'解绑成功")
            return True
