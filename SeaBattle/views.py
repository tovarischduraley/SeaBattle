from django.shortcuts import redirect, render


def register(request):
   if request.method== 'POST':
       form=UserForm(request.POST)
       if form.is_valid():
           user=User.objects.create_user(
               username=form.cleaned_data['username'],
               password=form.cleaned_data['password']
           )
           user.save()
           return redirect('index')
   else:
       form=UserForm()
   return render(request,'btlship/register.html',{'form':form})