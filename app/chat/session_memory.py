class SessionMemory:

    _sessions = {}

    @classmethod
    def get_history(
        cls,
        session_id
    ):

        return cls._sessions.get(
            session_id,
            []
        )

    @classmethod
    def add_message(
        cls,
        session_id,
        role,
        content
    ):

        if session_id not in cls._sessions:

            cls._sessions[
                session_id
            ] = []

        cls._sessions[
            session_id
        ].append(
            {
                "role": role,
                "content": content
            }
        )

    @classmethod
    def clear(
        cls,
        session_id
    ):

        if session_id in cls._sessions:

            del cls._sessions[
                session_id
            ]