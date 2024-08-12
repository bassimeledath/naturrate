from openai import OpenAI


class OpenAIModel:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_prompt(self, input_description: str) -> str:
        prompt = f"""
        As a skilled nature documentary narrator in the style of David Attenborough, your task is to create a concise, engaging narration script for a short nature video. The input will provide a description of the video content with timestamps and chapters. Your output should be a cohesive narration that matches the content and timing of the video.

        Instructions:
        1. Write only the narration text, without any timestamps or section headers.
        2. Ensure the length of each part of your narration corresponds to the given timestamps. Assume a speaking rate of about 2-3 words per second.
        3. Use vivid, descriptive language that brings the scene to life.
        4. Maintain a tone of wonder and respect for nature throughout the narration.
        5. Create smooth transitions between sections for a cohesive narrative.
        6. Keep the overall narration concise and impactful.

        Here are three examples of input descriptions and their corresponding output narrations:

        Example 1:
        Input:
        Chapter 0
        Start: 0 seconds
        End: 12 seconds
        Title: Vibrant Coral Garden
        Summary: The video opens with a stunning view of a colorful coral reef. Various species of coral in shades of purple, orange, and blue sway gently in the current. Small, brightly colored fish dart in and out of the coral structures, creating a lively underwater scene.

        Chapter 1
        Start: 12 seconds
        End: 30 seconds
        Title: Marine Life Interactions
        Summary: A sea turtle glides into frame, gracefully swimming through the coral. It pauses to nibble on some seagrass, showcasing the interconnected ecosystem. In the background, a school of silver fish moves in unison, creating a mesmerizing display of synchronized movement against the vibrant coral backdrop.

        Output:
        "A vibrant reef, teeming with life, where fish dance through coral gardens.
        A sea turtle grazes, as silver fish glide in unison, a testament to the ocean’s harmony."

        Example 2:
        Input:
        Chapter 0
        Start: 0 seconds
        End: 30 seconds
        Title: The Power of Nature Unleashed
        Summary: The video captures the intensity of a desert sandstorm. It begins with a calm desert landscape, featuring rolling sand dunes and a few sparse shrubs. Suddenly, the wind picks up, and sand begins to swirl. The camera pans to show the approaching wall of sand, which gradually engulfs the entire frame. The final moments reveal the raw power of the sandstorm, with visibility reduced to near zero as sand particles fill the air.

        Output:
        "Calm turns to chaos as a sandstorm rises, swallowing the desert in a swirling embrace of nature’s fury."

        Example 3:
        Input:
        Chapter 0
        Start: 0 seconds
        End: 10 seconds
        Title: Treetop Panorama
        Summary: The video starts with a sweeping view of a lush rainforest canopy. Sunlight filters through the dense foliage, creating a dappled effect on the leaves below. A colorful toucan perches on a nearby branch, its vibrant beak contrasting with the green surroundings.

        Chapter 1
        Start: 10 seconds
        End: 20 seconds
        Title: Primate Playground
        Summary: A family of capuchin monkeys swings into view, leaping from branch to branch with incredible agility. The camera follows their playful antics as they chase each other through the treetops, showcasing the complex three-dimensional environment of the rainforest canopy.

        Chapter 2
        Start: 20 seconds
        End: 30 seconds
        Title: Microcosm of Life
        Summary: The final chapter zooms in on a large bromeliad nestled in the crook of a tree branch. As the camera gets closer, it reveals a tiny ecosystem within the plant's water-filled center, including tadpoles, insects, and miniature frogs, highlighting the incredible biodiversity of the rainforest.

        Output:
        "A toucan rests high above, its colors vibrant against green.
        Capuchins swing through the canopy, a lively dance in the treetops."

        Now, create a narration for the following input:

        {input_description}
        """
        return prompt

    def generate_narration(self, chapters_text: str) -> str:
        prompt = self.generate_prompt(chapters_text)
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                    "content": "You are a skilled nature documentary narrator."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
