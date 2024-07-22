from sqlalchemy.orm import Session

from backend import models
from backend.db import db
from backend.logging import logger


class PaymentDeviceLock:

    def __init__(self, payment_device_id):
        self.session = None
        self.payment_device_id = payment_device_id
        self.is_locking = False

    def acquire(self, session: Session = None) -> bool:
        """ Tries to acquire database lock based on payment device ID.

        :param session: Allows the session to be instantiated and used outside the scope of this function.
        :return: True if lock is acquired otherwise False
        """
        self.session = session or db.create_session()
        try:
            db_lock = self.session.query(models.PaymentDeviceLock) \
                .filter(models.PaymentDeviceLock.id == self.payment_device_id) \
                .with_for_update() \
                .first()

            self.is_locking = db_lock is not None
            if self.is_locking is None:
                raise Exception('Locking record is missing and must be manually added.')
        except (Exception,):
            logger.exception(f'Failed to acquire lock for payment device {self.payment_device_id}')
            self.session.commit()
            self.is_locking = False
        finally:
            return self.is_locking

    def release(self):
        if self.is_locking:
            self.session.commit()
            self.is_locking = False


# lock = PaymentDeviceLock(1)
# if not lock.acquire():
#     return
#
# try:
#     pass
# except:
#     pass
# finally:
#     lock.release()
