---
layout: default
title: Previous Talks
nav_order: 4
---

# Previous Talks

<span class="section-label">Archive</span>

<div class="talks-list">
  {% assign has_previous = false %}
  {% for talk in site.data.talks reversed %}
    {% if talk.type == 'previous' %}
      {% assign has_previous = true %}
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
          <div>Session not recorded on request</div>
        {% endif %}
        {% if talk.abstract %}
          <div class="talk-subtitle">Questions</div>
          <div>Add questions under the <a href="https://www.youtube.com/@ENGAI-Exchange" target="_blank" rel="noopener">YouTube video</a> or email an <a href="{{ 'organizers' | relative_url }}">organizer</a>.</div>
        {% endif %}
      </div>
    {% endif %}
  {% endfor %}
  {% unless has_previous %}
    <div class="talk-empty">
      <p>Previous talks will appear here as sessions are completed.</p>
    </div>
  {% endunless %}
</div>
