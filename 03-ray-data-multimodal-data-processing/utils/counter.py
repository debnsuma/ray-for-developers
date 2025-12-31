

class Counter:
    def __init__(self):
        self.count = 0  # <--- This is the "State"

    def increment(self):
        self.count += 1
        return self.count

    def get_count(self):
        return self.count

# Step 1:Create four Counter actors and increment each Counter once and get the results. These tasks all happen in parallel.
counters = [Counter() for _ in range(4)]
results1 = [c.increment() for c in counters]
print("Initial counts: ", results1)

# Step 2: Increment the first Counter five times. These tasks are executed sequentially and share state.
results2 = [counters[0].increment() for _ in range(5)]
print("Incremented first counter five times: ", results2)
_ = [c.get_count() for c in counters]
print("Get the counts: ", _)

# Step 3: Increment each Counter once and get the results. These tasks all happen in parallel.
results3 = [c.increment() for c in counters]
print("Look at the final counts after incrementing each counter once: ", results3)