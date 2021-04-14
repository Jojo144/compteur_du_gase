from datetime import date, timedelta
from django.template.loader import render_to_string
from django.db.models import Q

from base.models import get_local_settings, Activity, Mail


def check_activities():
    """
    Cette tâche vérifie s'il y a assez d'inscrit·es aux activités de l'épicerie.
    S'il n'y a pas assez de monde inscrit, des notifications sont envoyées par email.
    La veille de l'activité, un dernier mail est envoyé pour indiquer si l'activité est maintenue ou annulée.
    Se référer au fichier README.md pour obtenir plus d'informations pour mettre en oeuvre ce dispositif.
    """
    local_settings = get_local_settings()
    days_before_subscriptions_open = 7
    days_before_last_reminder = 3
    days_before_confirm_cancel_decision = 1
    to_address = local_settings.mail_mailinglist_address
    if not local_settings.use_activity_reminders:
        return
    if not to_address:
        print("Cannot send activities notifications: mail_mailinglist_address is unset in your configuration")
        return

    def send_notification(subject_template, body_template, days, cancel=False, data=None):
        activities = Activity.objects.filter(Q(date=date.today() + timedelta(days=days)))
        for activity in activities:
            payload = {"activity": activity}
            if data:
                payload += data
            if not activity.can_be_hold or cancel:
                if not activity.can_be_hold and cancel:
                    activity.canceled = True
                    activity.save()
                subject = ' '.join([local_settings.prefix_object_mail,
                                    render_to_string(subject_template, {
                                        "activity": activity
                                    }).strip()]).strip()
                print(f"Sending mail {subject}")
                message = render_to_string(body_template, {
                    "activity": activity,
                    "subscription_close_date": activity.date - timedelta(days=days_before_confirm_cancel_decision)})
                mail = Mail(subject=subject, message=message, kind=Mail.NOTIFICATION)
                mail.save()
                mail.send(local_settings, [local_settings.mail_mailinglist_address])

    # J - 7, première relance : envoyer un mail si il n'y a pas assez de permanencier / membre intéressé
    send_notification("base/mail_activity_01_subscribing_is_open_subject.txt",
                      "base/mail_activity_01_subscribing_is_open.txt",
                      days=days_before_subscriptions_open)

    # J - 3 : dernière relance : si il n'y a pas assez de permanencier/membre intéressé
    send_notification("base/mail_activity_02_not_enough_participants_subject.txt",
                      "base/mail_activity_02_not_enough_participants.txt",
                      days=days_before_last_reminder)

    # J - 1 : envoyer un mail pour confirmer / infirmer la permanence
    send_notification("base/mail_activity_03_confirm_or_cancel_activity_subject.txt",
                      "base/mail_activity_03_confirm_or_cancel_activity.txt",
                      days=days_before_confirm_cancel_decision,
                      cancel=True)
