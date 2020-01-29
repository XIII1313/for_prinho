import datetime
import asyncio
import my_gspread
import pro_eu_registration
from pro_eu_static_variables import schedule_log_channel_id, sign_in_channel_id, role_tier_one_id, role_tier_two_id, guild_id, client


def get_hour_and_minute() -> list:
    # return a list of current hour and minute
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    return [hour, minute]


async def give_role_text_channel_permissions(role_id, text_channel_id, **permissions):
    guild = await client.fetch_guild(guild_id)
    target_role = guild.get_role(role_id)
    target_channel = client.get_channel(text_channel_id)
    await target_channel.set_permissions(target_role, **permissions)


async def give_tier_send_messages_permission(role_id):
    await give_role_text_channel_permissions(role_id, sign_in_channel_id, read_messages=True, send_messages=True, read_message_history=True)


async def take_tier_send_messages_permission(role_id):
    await give_role_text_channel_permissions(role_id, sign_in_channel_id, read_messages=True, send_messages=False, read_message_history=True)


async def auto_lock_unlock_main():
    print("Starting loop for auto (un)lock.")
    await client.wait_until_ready()

    while True:
        now = get_hour_and_minute()
        hour = now[0]
        minute = now[1]
        weekday_index = datetime.datetime.today().weekday()

        # unlocking for tier 1
        if hour == 11 and minute == 0 and weekday_index != 5:
            print("schedule unlock")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            sign_in_channel = client.get_channel(sign_in_channel_id)

            await schedule_log_channel.send("Executing automatic unlock for tier 1...")

            my_gspread.refresh_google_tokens()
            answer = "Resetting the sign ups ..."
            await schedule_log_channel.send(answer)
            pro_eu_registration.delete_column(my_gspread.signed_team_sheet, 1)
            await pro_eu_registration.edit_signed_team_message([])
            pro_eu_registration.set_reset_indicator(0)
            answer = "Reset done."
            await schedule_log_channel.send(answer)

            pro_eu_registration.set_lock_indicator(0)

            answer = "Changing permissions for tier 1 role."
            await schedule_log_channel.send(answer)
            await give_tier_send_messages_permission(role_tier_one_id)

            inform_team_captain_message = "Registration is now open for <@&{}>.".format(role_tier_one_id)
            await sign_in_channel.send(inform_team_captain_message)

            answer = "Automatic unlock complete for tier 1."
            await schedule_log_channel.send(answer)

            print("Going to sleep...")
            await asyncio.sleep(2 * 60 * 60)  # sleeps 2 hours

        # unlocking for tier 2
        elif hour == 14 and minute == 0 and weekday_index != 5:
            print("schedule unlock")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            sign_in_channel = client.get_channel(sign_in_channel_id)

            await schedule_log_channel.send("Executing automatic unlock for tier 2...")

            answer = "Changing permissions for tier 2 role."
            await schedule_log_channel.send(answer)
            await give_tier_send_messages_permission(role_tier_two_id)

            inform_team_captain_message = "Registration is now open for <@&{}>.".format(role_tier_two_id)
            await sign_in_channel.send(inform_team_captain_message)

            answer = "Automatic unlock complete for tier 2."
            await schedule_log_channel.send(answer)

            print("Going to sleep...")
            await asyncio.sleep(3 * 60 * 60)  # sleeps 3 hours

        # locking
        elif hour == 18 and minute == 0 and weekday_index != 5:
            print("schedule lock")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            sign_in_channel = client.get_channel(sign_in_channel_id)
            await schedule_log_channel.send("Executing automatic lock...")
            
            answer = "Changing permissions for tier 1 and tier 2 role."
            await schedule_log_channel.send(answer)
            await take_tier_send_messages_permission(role_tier_one_id)
            await take_tier_send_messages_permission(role_tier_two_id)
            
            my_gspread.refresh_google_tokens()
            pro_eu_registration.set_lock_indicator(1)

            inform_team_captain_message = "Registration locked."
            await sign_in_channel.send(inform_team_captain_message)

            await schedule_log_channel.send("Automatic lock complete.")
            print("Going in a long sleep...")
            await asyncio.sleep(13 * 60 * 60)  # runs every 5 seconds

        else:
            print("sleep for 56 secs...")
            await asyncio.sleep(56)  # runs every 59 seconds
