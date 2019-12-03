from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils import timezone
from .forms import PostForm
from django.shortcuts import redirect
import json
from ibm_watson import ToneAnalyzerV3
from ibm_watson import LanguageTranslatorV3

language_translator = LanguageTranslatorV3(
    version='2018-05-31',
    iam_apikey='TfhqK72GPR7RvfRT10VcCF19lNRH8jD-KJCmzdW842e1',
    url='https://gateway.watsonplatform.net/language-translator/api')

service = ToneAnalyzerV3(
    version='2017-09-26',
    iam_apikey='vrDSKI6_jK9iDtvl755Z9ZtDhvRlYtMzRkskAO0XJVS7',
    url='https://gateway.watsonplatform.net/tone-analyzer/api')


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    for post in posts:
        posting = post.text

        translation = language_translator.translate(text=posting, model_id='en-es').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']


        toneObj = json.dumps(service.tone(tone_input=posting,content_type="text/plain").get_result(), indent=2)
        post.toneObj2 = json.loads(toneObj)

        try:
            post.tonename1 = post.toneObj2['document_tone']['tones'][0]['tone_name']
            post.score1 = post.toneObj2['document_tone']['tones'][0]['score']
            post.tonename2 = post.toneObj2['document_tone']['tones'][1]['tone_name']
            post.score2 = post.toneObj2['document_tone']['tones'][1]['score']

        except:
            pass

    return render(request, 'blog/post_list.html', {'posts': posts})




def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})



