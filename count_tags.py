with open(r'd:\new_program_1@\tracker_app\templates\tracker_app\admin_employee_profile.html', 'r') as f:
    content = f.read()

# Count if/endif pairs
if_count = content.count('{% if ')
elif_count = content.count('{% elif ')
else_count = content.count('{% else %}')
endif_count = content.count('{% endif %}')

print(f'if count: {if_count}')
print(f'elif count: {elif_count}')
print(f'else count: {else_count}')
print(f'endif count: {endif_count}')

# Count for/endfor pairs
for_count = content.count('{% for ')
empty_count = content.count('{% empty %}')
endfor_count = content.count('{% endfor %}')

print(f'for count: {for_count}')
print(f'empty count: {empty_count}')
print(f'endfor count: {endfor_count}')