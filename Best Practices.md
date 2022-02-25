#Code collaboration best pratices
1. Use github with caution, and create non-github local backups as a failsafe
2. Communicate what files you are editing and how, and avoid stepping on each others toes. 
   1. This is especially important for UI files and major updates. 
   2. In these cases try to make sure other teammates
       hold off from editing that file until it is in the main branch. 
   3. Avoid having to merge .ui or QT-generated .py files.
3. Always pull changes from your own branch at the beginning of the day 
    (especially if you work on multiple machines)
4. Always commit to the branch with your first name
   1. Always commit and push each time you reach a stopping point or at the end of the day
   2. If there are bugs or other issues describe them in the commit description
5. When a feature is completed and working properly, create a pull request.
   1. Merge the PR automatically if possible, if not wait to merge together
   2. If waiting to merge you can still add commits to your branch

