---
layout: default
title: Organizers
nav_order: 6
---

# Organizers

<span class="section-label">Team</span>

<div class="people-container">
  {% for person in site.data.organizers %}
    <div class="people-card">
      <img class="person-image" src="{{ person.image | relative_url }}" alt="{{ person.name }}">
      <div class="person-high">{{ person.name }}</div>
      {% if person.email %}<div><a href="mailto:{{ person.email }}">{{ person.email }}</a></div>{% endif %}
      {% if person.website and person.website != "" %}<div>{{ person.website }}</div>{% endif %}
      {% if person.position and person.position != "" %}<div>{{ person.position }}</div>{% endif %}
      {% if person.institution %}<div>{{ person.institution }}</div>{% endif %}
      <div class="person-high">Bio</div>
      <div class="person-card-bio">{{ person.bio }}</div>
    </div>
  {% endfor %}
</div>

## Founding members

- Aliyu Kasimu  
- Franklin Eze  
- Ahmed Jamiu Opeyemi
