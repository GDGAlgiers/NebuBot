from discord.ext import commands

class UnknownError(commands.errors.CheckFailure):
    pass

class InvalidTeamName(commands.errors.CheckFailure):
    pass

class AuthorizationError(commands.errors.CheckFailure):
    pass

class HackTheBotNotRegistered(commands.errors.CheckFailure):
    pass