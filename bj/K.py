import multiprocessing
import time

def predict_worker(model_predict_func, data, result_queue):
    """Worker function that runs prediction in separate process"""
    try:
        result = model_predict_func(data)
        result_queue.put(('success', result))
    except Exception as e:
        result_queue.put(('error', str(e)))

def predict_with_timeout(model, data, timeout=2.0, default_value=-1.0):
    """
    Simple prediction with true timeout and process termination
    """
    # Create communication queue
    result_queue = multiprocessing.Queue()
    
    # Start prediction in separate process
    process = multiprocessing.Process(
        target=predict_worker,
        args=(model.predict, data, result_queue)
    )
    process.start()
    
    try:
        # Wait for result with timeout
        result_type, result = result_queue.get(timeout=timeout)
        process.join()  # Clean shutdown
        
        if result_type == 'success':
            return result
        else:
            print(f"Prediction error: {result}")
            return default_value
            
    except Exception:  # This catches Queue.Empty timeout
        print(f"Prediction timed out after {timeout} seconds - terminating process")
        process.terminate()  # Forcefully kill the process
        process.join(timeout=1)
        
        # If process is still alive, force kill
        if process.is_alive():
            process.kill()
            process.join()
            
        return default_value

# Example usage:
class SlowModel:
    def predict(self, data):
        time.sleep(3)  # Simulate slow prediction
        return 0.75

# This will timeout and kill the process
model = SlowModel()
result = predict_with_timeout(model, "test_data", timeout=1.0)
print(f"Result: {result}")  # Will print -1.0 due to timeout
