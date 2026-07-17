---
layout: default
title: Upcoming Talks
nav_order: 3
---

# Upcoming Talks

<span class="section-label">Schedule</span>

<div class="talks-list">
  {% assign has_upcoming = false %}
  {% for talk in site.data.talks %}
    {% if talk.type == 'upcoming' %}
      {% assign has_upcoming = true %}
      <div class="talk-container">
        <h3 class="talk-presenter">({{ talk.date }}) {{ talk.speaker }}</h3>
        <h4>{{ talk.institution }}</h4>
        {% if talk.title %}
          <div class="talk-subtitle">Title</div>
          <div>{{ talk.title }}</div>
        {% endif %}
        {% if talk.abstract %}
          <div class="talk-subtitle">Abstract</div>
          <div>{{ talk.abstract }}</div>
        {% endif %}
        {% if talk.bio %}
          <div class="talk-subtitle">Bio</div>
          <div>{{ talk.bio }}</div>
        {% endif %}
        {% if talk.recording %}
          <div class="talk-subtitle">Video</div>
          <div><a href="{{ talk.recording }}">Video recording</a></div>
        {% elsif talk.livestream %}
          <div class="talk-subtitle">Video</div>
          <div><a href="{{ talk.livestream }}">Livestream link</a></div>
        {% elsif talk.abstract %}
          <div class="talk-subtitle">Video</div>
          <div>Coming soon</div>
        {% endif %}
        {% if talk.abstract %}
          <div class="talk-subtitle">Questions</div>
          <div>Add questions under the <a href="https://www.youtube.com/@ENGAI-Exchange" target="_blank" rel="noopener">YouTube video</a> or email an <a href="{{ 'organizers' | relative_url }}">organizer</a>.</div>
        {% endif %}
      </div>
    {% endif %}
  {% endfor %}
  {% unless has_upcoming %}
    <div class="talk-empty">
      <p>No upcoming talks scheduled yet. Check back soon, or <a href="{{ 'nominate' | relative_url }}">nominate a speaker</a>.</p>
    </div>
  {% endunless %}
</div>
