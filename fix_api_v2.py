import sys

path = 'api.py'
with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
inserted = False
for line in lines:
    if 'await self.app(scope, receive, send)' in line and not inserted:
        new_lines.append(line)
        new_lines.append('\n')
        new_lines.append('app.add_middleware(ActivityTrackerMiddleware)\n')
        new_lines.append('\n')
        new_lines.append('async def shard_maintenance_loop():\n')
        new_lines.append('    iteration = 0\n')
        inserted = True
    else:
        new_lines.append(line)

with open(path, 'w') as f:
    f.writelines(new_lines)
print("api.py fully restored.")
