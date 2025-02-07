[Home](README.md)

# Credits and Disclaimer

The entire project is based on the work of NeuralNine (Florian Dedov) who in turn, was inspired
by the work of the YouTuber Cheesy AI while I was looking for something that demonstrates the use
of the NEAT algorithm in Python.

At first, the idea was that I was going to do everything from scratch... write my own game loop,
implement my own AI gent that would eventually lear how to steer a car around a simple circuit, etc.

But I soon figured out the amount of work that would invevitably have to go into such a project and
the time it would take to complete it - between family, work and my 2nd round of masters, time I
didn't have.

So I chose what I thought was simple enough to get me started, yet captured the essence of my project
which is to explore the NEAT algorithm, specifically its Python implementation, aptly named NEAT-Python.

At first, I started making small modifications to the original main file `newcar.py`. Then I realzied
with all the features I wanted to add, this would get complicated - fast! So I started separating
the logic in separate modules and throw a bit of OOP in the mix.

My intention was good, but my effort not so much. As I approached my deadline more and more, I found
myself making too many excuses and mixed program logic from one module to another. One such example is
the so called `neural_network.py` module... There's so much in it that doesn't belong there in the
first place...

While I was basically experimenting with the features of NEAT-Python, I was also learning how to use
PyGame. What I especially don't like how I handled it, was the 'random obstacles functionality',
specifically, the 'bounding zone' workaround.

Then, the code itself is not that Pythonic - if at all!?

I'll refactor later - or at least, that was my excuse.

My point is, **there's plenty of work to be done to make the code itself right and refactor it**.
For myself personally, I'll probably leave it as it is but you're more than welcomed to clone it and
refactor/modify it yourself.

I already got my benefit - the experience and pleasure of learning something new.

This project was heavily inspired from (well, not just 'inspired' but built on top of):

- [NeuralNine's work](https://github.com/NeuralNine/ai-car-simulation)

... but also from:

- [Hilicot's work](https://github.com/Hilicot/Neural_Network_NEAT)

I especially liked the live rendering of the NN that Hilicot has done. I really wanted to implement
something similar but there was not enough time. I had to close the project.

Perhaps some other time.

[Home](README.md)
