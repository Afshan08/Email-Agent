from django import forms

class QueryForm(forms.Form):
    query = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5, "cols": 80}),
        label="Your Query",
        required=True,
    )