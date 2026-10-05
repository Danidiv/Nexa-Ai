from core.models.lm_studio import LMStudioGateway


def main():
    model = LMStudioGateway()

    response = model.chat(
        [
            {
                "role": "user",
                "content": "Reply with exactly: Aziz V2 model gateway works."
            }
        ]
    )

    print()
    print("MODEL RESPONSE:")
    print(response)
    print()


if __name__ == "__main__":
    main()