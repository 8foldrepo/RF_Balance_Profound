list_test = ['2', '0', '2', '0', '0']
print(list_test)
print('This is our original list, loading new list...')
# list_test_2 = ['TRUE' for x in list_test if x == 2]
list_test_2 = ['FALSE' if '0' in x else 'TRUE' for x in list_test]
print(list_test_2)
print('Here is your new list with "FALSE" for values of 0 and "TRUE" for anything else')

