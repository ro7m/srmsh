import multiprocessing
import time

class KillableProcessPool:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.available_workers = multiprocessing.Semaphore(max_workers)
        self.active_processes = {}  # track active processes
    
    def submit_with_killable_timeout(self, func, *args, timeout=2.0, default_value=-1.0):
        """Submit task with true timeout that kills the process"""
        
        # Acquire worker (blocks if no workers available)
        if not self.available_workers.acquire(timeout=0.1):
            return default_value  # No workers available
        
        try:
            # Create result queue and process
            result_queue = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=self._worker_wrapper,
                args=(func, args, result_queue)
            )
            
            process.start()
            process_id = id(process)  # Simple ID
            self.active_processes[process_id] = process
            
            try:
                # Wait for result with timeout
                result = result_queue.get(timeout=timeout)
                process.join(timeout=0.1)  # Clean shutdown
                return result
                
            except Exception:  # Timeout or other error
                print(f"Timeout occurred - terminating process {process.pid}")
                
                # TRUE KILL - this actually stops the process
                process.terminate()  # SIGTERM
                process.join(timeout=0.1)
                
                # Force kill if still alive
                if process.is_alive():
                    process.kill()   # SIGKILL
                    process.join()
                
                return default_value
                
        finally:
            # Cleanup and release worker
            if process_id in self.active_processes:
                del self.active_processes[process_id]
            self.available_workers.release()
    
    def _worker_wrapper(self, func, args, result_queue):
        """Wrapper to catch exceptions and return results"""
        try:
            result = func(*args)
            result_queue.put(result)
        except Exception as e:
            result_queue.put(f"Error: {str(e)}")

# Usage:
pool = KillableProcessPool(max_workers=4)

def slow_prediction(data):
    time.sleep(5)  # Simulate slow ML prediction
    return 0.75

# This will timeout after 1 second and KILL the process
result = pool.submit_with_killable_timeout(
    slow_prediction, 
    "test_data", 
    timeout=1.0
)
print(f"Result: {result}")  # -1.0 (timeout), but process is actually killed
