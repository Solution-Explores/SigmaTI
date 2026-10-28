"""Liderança de coleta por advisory lock de sessão PostgreSQL."""
from sqlalchemy import text


class SchedulerLease:
    def __init__(self, engine):
        self.engine = engine
        self.connection = None

    def acquire(self):
        if self.connection is not None:
            try:
                self.connection.execute(text("SELECT 1"))
                self.connection.commit()
                return True
            except Exception:
                self.connection.invalidate()
                self.connection.close()
                self.connection = None
                return False
        connection = self.engine.connect()
        try:
            acquired = connection.scalar(text("SELECT pg_try_advisory_lock(7417003)"))
            connection.commit()
            if acquired:
                self.connection = connection
                return True
        except BaseException:
            connection.invalidate()
            raise
        finally:
            if self.connection is not connection:
                connection.close()
        return False

    def release(self):
        connection, self.connection = self.connection, None
        if connection is not None:
            try:
                connection.execute(text("SELECT pg_advisory_unlock(7417003)"))
                connection.commit()
            except Exception:
                connection.invalidate()
            finally:
                connection.close()
