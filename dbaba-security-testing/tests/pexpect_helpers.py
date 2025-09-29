"""
Helper functions for interacting with DBABA using pexpect.
"""
import pexpect
import time
from pathlib import Path


class DBABAClient:
    """Client for interacting with DBABA via pexpect."""
    
    def __init__(self, dbaba_path, working_dir, timeout=10):
        self.dbaba_path = dbaba_path
        self.working_dir = working_dir
        self.timeout = timeout
        self.process = None
        self.current_user = None
    
    def start(self):
        """Start the DBABA process."""
        if self.process is not None:
            self.stop()
        
        self.process = pexpect.spawn(
            "python3",
            [str(self.dbaba_path)],
            cwd=str(self.working_dir),
            timeout=self.timeout
        )
        self.process.expect("ABA>")
        return self
    
    def stop(self):
        """Stop the DBABA process."""
        if self.process is not None:
            self.process.terminate()
            self.process = None
        self.current_user = None
    
    def send_command(self, command, expect_prompt=True):
        """Send a command and return the output."""
        if self.process is None:
            raise RuntimeError("DBABA process not started")
        
        self.process.sendline(command)
        if expect_prompt:
            self.process.expect("ABA>")
        
        # Get the output before the prompt
        output = self.process.before.decode('utf-8').strip()
        return output
    
    def login(self, username, password=None, is_first_login=False):
        """Login to DBABA."""
        output = self.send_command(f"LIN {username}")
        
        if "Enter your password:" in output:
            # Not first login
            self.process.sendline(password)
            self.process.expect("ABA>")
            result = self.process.before.decode('utf-8').strip()
            if "OK" in result:
                self.current_user = username
            return result
        elif "create a new password" in output:
            # First login
            if password is None:
                password = "TestPass123"
            self.process.sendline(password)
            self.process.expect("Reenter the same password:")
            self.process.sendline(password)
            self.process.expect("ABA>")
            result = self.process.before.decode('utf-8').strip()
            if "OK" in result:
                self.current_user = username
            return result
        else:
            return output
    
    def logout(self):
        """Logout from DBABA."""
        output = self.send_command("LOU")
        if "OK" in output:
            self.current_user = None
        return output
    
    def change_password(self, new_password):
        """Change password for current user."""
        return self.send_command("CHP")
    
    def add_user(self, username):
        """Add a new user (admin only)."""
        return self.send_command(f"ADU {username}")
    
    def delete_user(self, username):
        """Delete a user (admin only)."""
        return self.send_command(f"DEU {username}")
    
    def list_users(self):
        """List all users (admin only)."""
        return self.send_command("LSU")
    
    def add_record(self, record_id, **fields):
        """Add a record."""
        field_str = " ".join([f"{k}={v}" for k, v in fields.items()])
        command = f"ADR {record_id} {field_str}".strip()
        return self.send_command(command)
    
    def read_record(self, record_id, *fields):
        """Read a record."""
        field_str = " ".join(fields)
        command = f"RER {record_id} {field_str}".strip()
        return self.send_command(command)
    
    def read_all_records(self, *fields):
        """Read all records."""
        field_str = " ".join(fields)
        command = f"REA {field_str}".strip()
        return self.send_command(command)
    
    def delete_record(self, record_id):
        """Delete a record."""
        return self.send_command(f"DER {record_id}")
    
    def export_database(self, filename):
        """Export database to file."""
        return self.send_command(f"EXD {filename}")
    
    def import_database(self, filename):
        """Import database from file."""
        return self.send_command(f"IMD {filename}")
    
    def who_am_i(self):
        """Get current user."""
        return self.send_command("WAI")
    
    def read_audit_log(self, username=None):
        """Read audit log (admin only)."""
        if username:
            return self.send_command(f"RAL {username}")
        else:
            return self.send_command("RAL")
    
    def delete_audit_log(self, username=None):
        """Delete audit log (admin only)."""
        if username:
            return self.send_command(f"DAL {username}")
        else:
            return self.send_command("DAL")
    
    def help(self):
        """Get help."""
        return self.send_command("HLP")
    
    def exit(self):
        """Exit DBABA."""
        return self.send_command("EXT")
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def create_test_csv_file(temp_dir, filename, records):
    """Create a test CSV file with the given records."""
    filepath = Path(temp_dir) / filename
    with open(filepath, 'w') as f:
        for record in records:
            f.write(record + '\n')
    return filepath


def wait_for_lockout_expiry(seconds=65):
    """Wait for account lockout to expire."""
    time.sleep(seconds)
