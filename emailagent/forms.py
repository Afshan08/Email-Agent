from django import forms

class AgentReplyForm(forms.Form):
    response = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
        label="Suggested Reply",
        required=True,
    )