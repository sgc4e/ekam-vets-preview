import re

ICO = {
 'homeo':'<path d="M12 3c3.5 3.2 5.5 6 5.5 8.6A5.5 5.5 0 0 1 12 17a5.5 5.5 0 0 1-5.5-5.4C6.5 9 8.5 6.2 12 3z"/><path d="M12 17v4"/>',
 'herb':'<path d="M12 21c0-6 3.5-10 8-11-.5 6-4 10-8 11z"/><path d="M12 21c0-5-3-8.5-7-9.5.4 5 3.4 8.5 7 9.5z"/><path d="M12 21v-6"/>',
 'hands':'<path d="M8 13V6a1.6 1.6 0 0 1 3.2 0v5"/><path d="M11.2 11V5a1.6 1.6 0 0 1 3.2 0v6"/><path d="M14.4 11.5V7.5a1.6 1.6 0 0 1 3.2 0V14a7 7 0 0 1-7 7 6 6 0 0 1-6-6l-1-3.2a1.6 1.6 0 0 1 2.8-1.5L8 13"/>',
 'senior':'<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/><path d="M9 20.5c2-1 4-1 6 0"/>',
}
def ico(k): return '<span class="ico"><svg viewBox="0 0 24 24">%s</svg></span>' % ICO[k]

# ---------------- home bento ----------------
f='index.html'; s=open(f,encoding='utf-8').read()

new_tiles = """
      <div class="b mint">
        %s
        <h3>Homeopathy</h3>
        <p>Prescribed inside the consult by a registered veterinary surgeon, alongside the medicine and never in place of it. Used where a gentle option helps: chronic skin, anxiety, slow recovery, older animals already carrying a heavy drug load.</p>
        <a class="more" href="services.html#homeopathy">Learn more</a>
      </div>

      <div class="b">
        %s
        <h3>Herbal and natural medicine</h3>
        <p>Plant based preparations for skin, digestion and stiff joints. We tell you what is in it, what it costs, and what we expect in two weeks. If it does not do that, we stop it.</p>
        <a class="more" href="services.html#herbal">Learn more</a>
      </div>

      <div class="b shell">
        %s
        <h3>Massage and acupuncture</h3>
        <p>Hands on work and needling for pain, stiffness and nerve cases, run alongside physiotherapy. Useful in older dogs and in animals we are trying to move off long term painkillers.</p>
        <a class="more" href="services.html#massage">Learn more</a>
      </div>

      <div class="b wide">
        %s
        <h3>Senior and palliative care</h3>
        <p>Animals over eight need a different visit. Twice yearly bloods, a pain plan, a weight and mobility target, and a diet that matches failing kidneys or a tired heart. When the time comes, an honest conversation about the last few weeks, at home if you want it that way.</p>
        <a class="more" href="services.html#senior">Learn more</a>
      </div>
""" % (ico('homeo'), ico('herb'), ico('hands'), ico('senior'))

anchor = '''      <div class="b ink wide">'''
assert anchor in s
s = s.replace(anchor, new_tiles + '\n' + anchor, 1)
s = s.replace('<p>Care that addresses the whole animal, not only the symptom in front of us.</p>',
              '<p>Nine kinds of care, one team, one file. Medicine leads and everything else is layered on top of it.</p>',1)
open(f,'w',encoding='utf-8').write(s); print('home bento: 4 tiles added')

# ---------------- services page ----------------
f='services.html'; s=open(f,encoding='utf-8').read()
NEW = """
<section class="tint" id="homeopathy">
  <div class="wrap">
    <div class="split">
      <div>
        <p class="eyebrow">05</p>
        <h2>Homeopathy</h2>
        <p>Homeopathic remedies are prescribed here inside the veterinary consult, by a registered veterinary surgeon, as one part of a written plan. They sit alongside the medicine. They do not replace it.</p>
        <p>Where we use them: chronic skin that keeps returning, anxiety and travel stress, slow recovery in older animals, and cases where an animal is already carrying a heavy drug load we would like to reduce.</p>
        <p>Where we do not: infection, trauma, poisoning, an animal that is dehydrated or in pain right now. Those get medicine, immediately, and we will say so plainly.</p>
      </div>
      <div>
        <div class="card">
          <h3>What we will tell you</h3>
          <ul class="ticks">
            <li>What the remedy is and what it costs</li>
            <li>What we expect to see, and by when</li>
            <li>What the conventional option is, so you can choose</li>
            <li>When we will stop it, if nothing changes</li>
          </ul>
          <p class="note">No animal is put on a homeopathic plan alone when a conventional treatment is the right answer.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="herbal">
  <div class="wrap">
    <div class="split">
      <div>
        <div class="card">
          <h3>Where herbs earn their place</h3>
          <ul class="ticks">
            <li>Skin washes for recurring itch and hot spots</li>
            <li>Digestive support after a long antibiotic course</li>
            <li>Joint support in older animals, with physiotherapy</li>
            <li>Wound and coat care between visits</li>
            <li>Appetite and gut settling in convalescence</li>
          </ul>
        </div>
      </div>
      <div>
        <p class="eyebrow">06</p>
        <h2>Herbal and natural medicine</h2>
        <p>Plant based preparations, used where they help and named where they are used. You get told what is in it, what it costs, and what we expect it to do in two weeks.</p>
        <p>If it does not do that, we stop it. A remedy that is still on the prescription six months later because nobody reviewed it is not natural care, it is a subscription.</p>
        <p>Herbs interact with drugs. Tell us everything your animal is already taking, including anything bought off a shelf.</p>
      </div>
    </div>
  </div>
</section>

<section class="tint" id="massage">
  <div class="wrap">
    <div class="split">
      <div>
        <p class="eyebrow">07</p>
        <h2>Massage and acupuncture</h2>
        <p>Hands on soft tissue work and needling for pain, stiffness and nerve cases. Run alongside physiotherapy in the same course, never sold as a standalone package.</p>
        <p>Most useful in older dogs with hip and spine pain, in post-surgical stiffness, and in animals on long term painkillers we are trying to reduce.</p>
        <p>Sessions are twenty to thirty minutes. Some animals settle into it and sleep. Some do not tolerate needling at all, and when that happens we say so and stop rather than sell you a course.</p>
      </div>
      <div>
        <div class="card">
          <h3>Typical cases</h3>
          <ul class="ticks">
            <li>Hip and spine pain in dogs over eight</li>
            <li>Stiffness four to eight weeks after surgery</li>
            <li>Disc and nerve cases past the acute phase</li>
            <li>Muscle wastage on one side after a limp</li>
            <li>Anxious animals who hold tension in the neck and back</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="senior">
  <div class="wrap">
    <div class="split">
      <div>
        <div class="card">
          <h3>The senior visit</h3>
          <ul class="ticks">
            <li>Bloods twice a year, not once a crisis</li>
            <li>Kidney, liver and thyroid tracked over time</li>
            <li>A written pain score you can repeat at home</li>
            <li>Weight and mobility targets with numbers</li>
            <li>Diet matched to what the organs can still do</li>
            <li>Dental review, because a bad mouth ages an animal fast</li>
          </ul>
        </div>
      </div>
      <div>
        <p class="eyebrow">08</p>
        <h2>Senior and palliative care</h2>
        <p>An animal over eight needs a different kind of visit. Not more tests. Different ones, twice a year, tracked against the last set so we can see the line rather than the dot.</p>
        <p>And when treatment stops being the kind thing, we will say that too. A pain plan, a comfort plan, and an honest conversation about the last few weeks. At home, if that is where your animal is calm.</p>
        <p>Nobody in this part of Jaipur is doing this properly. We think that is the gap that matters most.</p>
      </div>
    </div>
  </div>
</section>
"""
anchor = '<section class="dark watermark">'
assert anchor in s
s = s.replace(anchor, NEW + '\n' + anchor, 1)
open(f,'w',encoding='utf-8').write(s); print('services: 4 sections added')

# ---------------- rate card ----------------
f='rates.html'; s=open(f,encoding='utf-8').read()
TABLE = """        <table class="rates">
          <caption>Homeopathy, herbs and bodywork</caption>
          <tr><th>Service</th><th style="text-align:right">Price</th></tr>
          <tr><td>Homeopathic prescription<small>Inside the consult, remedy included</small></td><td class="price">Rs 250</td></tr>
          <tr><td>Herbal preparation, per course<small>By preparation and animal size</small></td><td class="price">Rs 400 to 900</td></tr>
          <tr><td>Massage or acupuncture session<small>Twenty to thirty minutes</small></td><td class="price">Rs 600</td></tr>
          <tr><td>Course of 6 bodywork sessions<small>With a physiotherapy plan</small></td><td class="price">Rs 3,200</td></tr>
        </table>

        <table class="rates">
          <caption>Senior and palliative</caption>
          <tr><th>Service</th><th style="text-align:right">Price</th></tr>
          <tr><td>Senior wellness package<small>Twice yearly bloods, pain score, diet and dental review</small></td><td class="price">Rs 3,200</td></tr>
          <tr><td>Palliative home visit<small>Within 5 km, comfort and pain plan</small></td><td class="price">Rs 1,200</td></tr>
        </table>

"""
anchor = '        <div class="card">\n          <h3>How billing works here</h3>'
assert anchor in s
s = s.replace(anchor, TABLE + anchor, 1)
open(f,'w',encoding='utf-8').write(s); print('rates: 2 tables added')

# ---------------- integrated care strand ----------------
f='integrated-care.html'; s=open(f,encoding='utf-8').read()
s = s.replace('<h3>Traditional and gentle remedies</h3>','<h3>Homeopathy and herbal medicine</h3>',1)
s = s.replace('<p>Where a mild, low side effect remedy works alongside the medicine, we use it. It supports the treatment. It never replaces a drug the animal needs.</p>',
              '<p>Homeopathic and plant based remedies, prescribed inside the consult by a registered veterinary surgeon. They support the treatment. They never replace a drug the animal needs.</p>',1)
s = s.replace('<h3>Physiotherapy and movement</h3>','<h3>Physiotherapy, massage and acupuncture</h3>',1)
open(f,'w',encoding='utf-8').write(s); print('integrated-care: strands updated')
