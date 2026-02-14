# Hierarchical strategy structure for improved classification accuracy
# This file contains the full structure with parent categories and subclasses

STRATEGIES_INFO = [
    # Exchange / Incentives (1-5)
    {
        "name": "Rewarding Activity",
        "description": "persuader promises or offers a reward, benefit, or special treatment if the other person agrees to donate.",
        "parent_category": "Exchange / Incentives",
        "parent_id": "exchange",
        "subclass_id": "reward_benefit",
        "subclass_name": "Reward / Benefit (Conditional Reward)",
        "markers": ["if you donate", "you'll get", "access", "prize", "bonus", "discount", "raffle"],
        "decision_rules": {
            "use_if": ["Text promises future benefit/reward IF person donates (conditional on donation)."],
            "avoid_if": ["No exchange element; only morality, fear, urgency, or facts.", "Gift was already given (use Pre-giving).", "Explicit promise of guarantee (use Promise)."]
        }
    },
    {
        "name": "Pre-giving",
        "description": "persuader gives or offers something first, or refers to a previous favor, and then asks the other person to donate in return.",
        "parent_category": "Exchange / Incentives",
        "parent_id": "exchange",
        "subclass_id": "pre_giving",
        "subclass_name": "Pre-giving (Gift First)",
        "markers": ["I already did", "I helped you", "here you go", "here's for you", "I did it for you"],
        "decision_rules": {
            "use_if": ["Text mentions gift/favor that was ALREADY given (past tense), then asks for donation."],
            "avoid_if": ["Only promised future reward (use Rewarding Activity).", "Explicit 'you owe' obligation (use Debt).", "Only mutual help reminder without gift (use Reciprocity)."]
        }
    },
    {
        "name": "Reciprocity",
        "description": "persuader reminds the other person that they have already done something for them and now expect a donation in return.",
        "parent_category": "Exchange / Incentives",
        "parent_id": "exchange",
        "subclass_id": "reciprocity",
        "subclass_name": "Reciprocity (Return Favor Reminder)",
        "markers": ["remember I", "helped you out", "mutually", "as a friend"],
        "decision_rules": {
            "use_if": ["Text reminds of past mutual help/favor without explicit gift, suggests return favor."],
            "avoid_if": ["Gift/favor was just given now (use Pre-giving).", "Explicit 'you owe me' language (use Debt).", "Only social obligation without personal favor (use Social Proof)."]
        }
    },
    {
        "name": "Debt",
        "description": "persuader suggests that the other person owes them something and therefore should donate.",
        "parent_category": "Exchange / Incentives",
        "parent_id": "exchange",
        "subclass_id": "debt_owed",
        "subclass_name": "Debt (You Owe)",
        "markers": ["you owe", "you must", "in debt", "pay back", "time to return"],
        "decision_rules": {
            "use_if": ["Text explicitly states person OWES something or uses debt/obligation language."],
            "avoid_if": ["No personal owing; only moral duty (use Norms/Morality parent).", "Mention of past favor without explicit debt (use Reciprocity)."]
        }
    },
    # Authority / Expertise (6-8)
    {
        "name": "Expertise",
        "description": "persuader presents themselves as knowledgeable or experienced and uses their expert status to convince the other person to donate.",
        "parent_category": "Authority / Expertise",
        "parent_id": "authority_expertise",
        "subclass_id": "expertise",
        "subclass_name": "Expertise (Personal Knowledge)",
        "markers": ["I understand", "I worked", "from experience", "I know how it works"],
        "decision_rules": {
            "use_if": ["Text emphasizes personal knowledge, experience, or professional expertise (first-person: 'I know', 'I've seen', 'in my experience')."],
            "avoid_if": ["No credibility/status cues; only emotions or urgency.", "Official position/organizational status is primary (use Authority).", "Focus is on transparency/verifiability without expertise (use Credibility Appeal)."]
        }
    },
    {
        "name": "Authority",
        "description": "persuader refers to their official position, status, or expert role to pressure the other person into donating.",
        "parent_category": "Authority / Expertise",
        "parent_id": "authority_expertise",
        "subclass_id": "authority_status",
        "subclass_name": "Authority (Official Status)",
        "markers": ["I'm a representative", "official collection", "administration", "regulations", "foundation"],
        "decision_rules": {
            "use_if": ["Text emphasizes official position, institutional role, or organizational status ('I represent', 'official collection', 'we are', 'foundation', 'organization')."],
            "avoid_if": ["No credibility/status cues; only emotions or urgency.", "Personal expertise/knowledge is primary (use Expertise).", "Only transparency claims without official status (use Credibility Appeal)."]
        }
    },
    {
        "name": "Credibility Appeal",
        "description": "persuader highlights their honesty, transparency, or trustworthiness to make the donation request more convincing.",
        "parent_category": "Authority / Expertise",
        "parent_id": "authority_expertise",
        "subclass_id": "credibility_trust",
        "subclass_name": "Credibility / Transparency",
        "markers": ["report", "receipts", "transparent", "proof", "evidence", "can verify"],
        "decision_rules": {
            "use_if": ["Text emphasizes transparency, verifiability, or trustworthiness ('you can check', 'transparent', 'can verify', 'receipts available', 'reports show')."],
            "avoid_if": ["No credibility/status cues; only emotions or urgency.", "Official position/organizational status is primary (use Authority).", "Personal expertise/knowledge is primary (use Expertise)."]
        }
    },
    # Norms / Morality / Values (9-13)
    {
        "name": "Moral Appeal",
        "description": "persuader argues that donating is morally right, good, or the ethically correct thing to do.",
        "parent_category": "Norms / Morality / Values",
        "parent_id": "norms_morality",
        "subclass_id": "moral_right_wrong",
        "subclass_name": "Moral Right/Wrong",
        "markers": ["it's right", "it's good", "can't do that", "by conscience", "sin"],
        "decision_rules": {
            "use_if": ["Text argues that donating is morally right, good, or ethically correct ('it's right', 'it's good', 'can't do that', 'by conscience')."],
            "avoid_if": ["Mainly numbers/impact or explicit exchange.", "Focus is duty/social norms (use Activation of Impersonal Commitment).", "Targets shame/guilt directly (use Guilt Induction).", "Appeals to person's values/ideals (use Appeal to Values)."]
        }
    },
    {
        "name": "Appeal to Values",
        "description": "persuader refers to the other person's core values, beliefs, or ideals to justify donating.",
        "parent_category": "Norms / Morality / Values",
        "parent_id": "norms_morality",
        "subclass_id": "values_identity",
        "subclass_name": "Appeal to Values (Ideals)",
        "markers": ["you value", "important to you", "you care", "you're for"],
        "decision_rules": {
            "use_if": ["Text refers to person's core values, beliefs, or ideals to justify donating ('you value', 'important to you', 'you care', 'you're for')."],
            "avoid_if": ["Mainly numbers/impact or explicit exchange.", "Uses past promise/consistency (use Commitment parent).", "Focus is on self-feeling/pride (use Self-feeling Appeal).", "Focus is moral right/wrong without personal values (use Moral Appeal)."]
        }
    },
    {
        "name": "Activation of Impersonal Commitment",
        "description": "persuader appeals to duties, rules, social norms, or moral obligations, arguing that donating is what one ought to do.",
        "parent_category": "Norms / Morality / Values",
        "parent_id": "norms_morality",
        "subclass_id": "duty_norms",
        "subclass_name": "Duty / Social Norms",
        "markers": ["must", "obligation", "everyone should", "it's customary", "our duty"],
        "decision_rules": {
            "use_if": ["Text appeals to duties, rules, social norms, or moral obligations ('must', 'obligation', 'everyone should', 'it's customary', 'our duty')."],
            "avoid_if": ["Mainly numbers/impact or explicit exchange.", "Direct shame/guilt attack (use Guilt Induction).", "Focus is moral right/wrong (use Moral Appeal)."]
        }
    },
    {
        "name": "Guilt Induction",
        "description": "persuader tries to make the other person feel guilty or ashamed for not donating or for considering not donating.",
        "parent_category": "Norms / Morality / Values",
        "parent_id": "norms_morality",
        "subclass_id": "guilt_shame",
        "subclass_name": "Guilt/Shame Induction",
        "markers": ["aren't you ashamed", "how can you", "disappointed", "you'll abandon"],
        "decision_rules": {
            "use_if": ["Text tries to make person feel guilty or ashamed for not donating ('aren't you ashamed', 'how can you', 'disappointed', 'you'll abandon')."],
            "avoid_if": ["Mainly numbers/impact or explicit exchange.", "Fear about external danger (use Threat/Pressure or Emotional parent).", "Just describes moral duty without guilt attack (use Activation of Impersonal Commitment)."]
        }
    },
    {
        "name": "Self-feeling Appeal",
        "description": "persuader suggests that donating will make the other person feel better about themselves, proud, or like a good person.",
        "parent_category": "Norms / Morality / Values",
        "parent_id": "norms_morality",
        "subclass_id": "values_identity",
        "subclass_name": "Appeal to Values (Self-feeling variant)",
        "markers": ["you value", "important to you", "you care", "you're for", "you'll feel", "pride"],
        "decision_rules": {
            "use_if": ["Text suggests donating will make person feel better about themselves, proud, or like a good person ('you'll feel', 'pride', 'feel good', 'good person')."],
            "avoid_if": ["Mainly numbers/impact or explicit exchange.", "Focus is on person's values/ideals (use Appeal to Values).", "Uses guilt/shame attack (use Guilt Induction)."]
        }
    },
    
    # Commitment / Consistency (15-18)
    {
        "name": "Activation of Personal Commitment",
        "description": "persuader reminds the other person about their past promises, intentions, or self-image in order to push them to donate now.",
        "parent_category": "Commitment / Consistency",
        "parent_id": "commitment",
        "subclass_id": "past_promise",
        "subclass_name": "Past Promise / Prior Intention",
        "markers": ["you promised", "you wanted", "you said you'd help", "we agreed"],
        "decision_rules": {
            "use_if": ["Text reminds person about their past promises, intentions, or self-image to push donation ('you promised', 'you wanted', 'you said you'd help', 'we agreed')."],
            "avoid_if": ["Only moral duty without personal past reference.", "Escalation from small request to big (use Foot-in-the-door).", "Focus is identity consistency without past promise (use Commitment and Consistency)."]
        }
    },
    {
        "name": "Commitment and Consistency",
        "description": "persuader stresses that the other person should act in line with their previous statements, values, or small agreements by donating now.",
        "parent_category": "Commitment / Consistency",
        "parent_id": "commitment",
        "subclass_id": "self_image",
        "subclass_name": "Self-Image Consistency",
        "markers": ["you're a good person", "you're not like that", "you always help", "this is about you"],
        "decision_rules": {
            "use_if": ["Text stresses person should act in line with previous statements, values, or small agreements ('you're a good person', 'you're not like that', 'you always help', 'this is about you')."],
            "avoid_if": ["Only moral duty without personal past reference.", "Focus is ideals/values rather than identity consistency (use Appeal to Values).", "Mentions specific past promise (use Activation of Personal Commitment)."]
        }
    },
    {
        "name": "Foot-in-the-door",
        "description": "persuader first gets the other person to agree to a small request and then escalates to asking for a donation or a larger amount.",
        "parent_category": "Commitment / Consistency",
        "parent_id": "commitment",
        "subclass_id": "past_promise",
        "subclass_name": "Past Promise / Prior Intention - Escalation variant",
        "markers": ["you promised", "you wanted", "first", "then", "now"],
        "decision_rules": {
            "use_if": ["Text first gets person to agree to small request then escalates to asking for donation or larger amount ('first', 'then', 'now', sequence of requests)."],
            "avoid_if": ["Only moral duty without personal past reference.", "No escalation sequence, just past promise reminder (use Activation of Personal Commitment)."]
        }
    },
    {
        "name": "Door-in-the-face",
        "description": "persuader starts with a very large or unreasonable request, expects a refusal, and then follows up with a smaller donation request that seems more acceptable.",
        "parent_category": "Commitment / Consistency",
        "parent_id": "commitment",
        "subclass_id": "past_promise",
        "subclass_name": "Past Promise / Prior Intention - Door-in-the-face variant",
        "markers": ["first", "then", "less"],
        "decision_rules": {
            "use_if": ["Text starts with very large/unreasonable request, expects refusal, then follows with smaller donation request ('first', 'then', 'less', sequence of decreasing requests)."],
            "avoid_if": ["Only moral duty without personal past reference.", "Escalation from small to big (use Foot-in-the-door)."]
        }
    },
    
    # Social Influence (19-21)
    {
        "name": "Social Proof",
        "description": "persuader emphasizes that many other people donate or support this cause, and therefore the listener should also donate.",
        "parent_category": "Social Influence",
        "parent_id": "social_influence",
        "subclass_id": "social_proof",
        "subclass_name": "Social Proof",
        "markers": ["already donated", "many supported", "everyone chipped in", "hundreds of people"],
        "decision_rules": {
            "use_if": ["Text emphasizes that many other people donate or support this cause ('already donated', 'many supported', 'everyone chipped in', 'hundreds of people')."],
            "avoid_if": ["No social comparison/belonging cues.", "Focus is 'we/us' shared identity (use Unity).", "Focus is labeling certain types of people (use Social Positioning)."]
        }
    },
    {
        "name": "Unity",
        "description": "persuader emphasizes a shared identity or group membership, presenting donating as something that 'people like us' do.",
        "parent_category": "Social Influence",
        "parent_id": "social_influence",
        "subclass_id": "unity_identity",
        "subclass_name": "Unity (Shared Identity)",
        "markers": ["we together", "ours", "people like us", "our own", "our community"],
        "decision_rules": {
            "use_if": ["Text emphasizes shared identity or group membership, presenting donating as what 'people like us' do ('we together', 'ours', 'people like us', 'our own', 'our community')."],
            "avoid_if": ["No social comparison/belonging cues.", "Only popularity/majority without 'we/us' identity (use Social Proof).", "Focus is labeling/social positioning (use Social Positioning)."]
        }
    },
    {
        "name": "Social Positioning",
        "description": "persuader implies that certain kinds of people donate and others do not, placing the listener in or out of a desired social group.",
        "parent_category": "Social Influence",
        "parent_id": "social_influence",
        "subclass_id": "social_positioning",
        "subclass_name": "Social Positioning (Labeling)",
        "markers": ["normal people", "decent", "who really", "don't be the one who"],
        "decision_rules": {
            "use_if": ["Text implies certain kinds of people donate and others do not, placing listener in or out of desired social group ('normal people', 'decent', 'who really', 'don't be the one who')."],
            "avoid_if": ["No social comparison/belonging cues.", "Direct guilt/shame attack (use Guilt Induction).", "Focus is 'we/us' shared identity (use Unity).", "Focus is popularity/majority (use Social Proof)."]
        }
    },
    
    # Rational / Impact Appeal (22-23)
    {
        "name": "Rational Appeal",
        "description": "persuader presents practical reasons, efficiency, or clear benefits to convince the other person to donate.",
        "parent_category": "Rational / Impact Appeal",
        "parent_id": "rational",
        "subclass_id": "facts_numbers",
        "subclass_name": "Facts & Numbers",
        "markers": ["statistics", "data shows", "research indicates", "studies show", "numbers prove", "percentage", "according to studies", "scientific evidence", "%", "€", "$", "numbers", "statistical"],
        "decision_rules": {
            "use_if": ["Text presents practical reasons, facts, or statistics to convince person to donate (numbers, percentages, data, statistics, research)."],
            "avoid_if": ["Pure emotional story without reasoning.", "Main point is time pressure (use Urgency/Scarcity parent).", "Focus is on efficiency/impact rather than facts (use Logical Appeal)."]
        }
    },
    {
        "name": "Logical Appeal",
        "description": "persuader builds a structured, logical argument, often with facts or numbers, to show why donating is the reasonable choice.",
        "parent_category": "Rational / Impact Appeal",
        "parent_id": "rational",
        "subclass_id": "efficiency_impact",
        "subclass_name": "Efficiency / Impact",
        "markers": ["every 10€", "maximum effect", "most effective", "impact", "matching"],
        "decision_rules": {
            "use_if": ["Text emphasizes efficiency, measurable impact, or cost-effectiveness ('every 10€', 'maximum effect', 'most effective', 'impact', 'matching')."],
            "avoid_if": ["Pure emotional story without reasoning.", "Mostly social proof or morality.", "Focus is on facts/statistics rather than impact (use Rational Appeal)."]
        }
    },
    
    # Emotional Influence (24-29)
    {
        "name": "Emotional Appeal",
        "description": "persuader tries to move the other person emotionally, for example by appealing to compassion, sadness, hope, or pride to get a donation.",
        "parent_category": "Emotional Influence",
        "parent_id": "emotional",
        "subclass_id": "empathy",
        "subclass_name": "Emotional Appeal (General)",
        "markers": ["pity", "suffering", "heart", "imagine", "crying", "story", "pain"],
        "decision_rules": {
            "use_if": ["Text uses emotional language to create feeling without specific technique (general emotional appeal, emotional words without narrative or perspective-taking)."],
            "avoid_if": ["Mainly facts, duty, exchange, or authority.", "Text explicitly asks to IMAGINE being in another's situation (use Empathy Appeal).", "Text describes suffering to elicit pity without imagination prompt (use Sympathy Appeal)."]
        }
    },
    {
        "name": "Storytelling",
        "description": "persuader tells a story or narrative, often about a person or situation, to emotionally illustrate why a donation is needed.",
        "parent_category": "Emotional Influence",
        "parent_id": "emotional",
        "subclass_id": "story",
        "subclass_name": "Storytelling",
        "markers": ["story", "yesterday", "with him", "she", "family", "child", "happened"],
        "decision_rules": {
            "use_if": ["Text tells a story or narrative, often about a person or situation, to emotionally illustrate why donation is needed ('story', 'yesterday', 'with him', 'she', 'family', 'child', 'happened')."],
            "avoid_if": ["Mainly facts, duty, exchange, or authority.", "Just perspective-taking without narrative (use Empathy Appeal).", "No narrative structure, just emotional words (use Emotional Appeal)."]
        }
    },
    {
        "name": "Empathy Appeal",
        "description": "persuader asks the other person to imagine the suffering or feelings of others and to donate out of compassion.",
        "parent_category": "Emotional Influence",
        "parent_id": "emotional",
        "subclass_id": "empathy",
        "subclass_name": "Empathy (Perspective Taking)",
        "markers": ["imagine", "put yourself", "how would you", "if it were your"],
        "decision_rules": {
            "use_if": ["Text explicitly asks person to IMAGINE being in another's situation ('imagine', 'put yourself', 'how would you', 'if it were your', 'what if it were you')."],
            "avoid_if": ["Mainly facts, duty, exchange, or authority.", "Only pity wording without perspective prompt (use Sympathy Appeal).", "Full story/narrative without imagination prompt (use Storytelling)."]
        }
    },
    {
        "name": "Sympathy Appeal",
        "description": "persuader highlights their own suffering or the hardship of others to make the listener feel sorry and want to donate.",
        "parent_category": "Emotional Influence",
        "parent_id": "emotional",
        "subclass_id": "sympathy",
        "subclass_name": "Sympathy / Pity",
        "markers": ["feel sorry for", "their suffering", "my hardship", "helpless", "in need", "struggling", "poor thing", "unfortunate situation", "terrible to see", "their pain"],
        "decision_rules": {
            "use_if": ["Text describes suffering/hardship to elicit pity/sympathy without asking person to imagine themselves in that situation."],
            "avoid_if": ["Mainly facts, duty, exchange, or authority.", "Text asks person to IMAGINE being in another's situation (use Empathy Appeal).", "Text attacks person's character or uses emotional blackmail (use Emotional Manipulation).", "Text uses guilt/shame targeting (use Guilt Induction)."]
        }
    },
    {
        "name": "Fear Appeal",
        "description": "persuader emphasizes risks, dangers, or negative outcomes that could happen if the other person or others do not donate.",
        "parent_category": "Emotional Influence",
        "parent_id": "emotional",
        "subclass_id": "sympathy",
        "subclass_name": "Fear Appeal (Emotional variant)",
        "markers": ["danger", "threat", "will happen", "could happen", "risks", "consequences", "terrible outcome", "disaster", "harm", "safety", "at risk"],
        "decision_rules": {
            "use_if": ["Text emphasizes risks, dangers, or negative outcomes that could happen if donation is not made."],
            "avoid_if": ["Mainly facts, duty, exchange, or authority.", "Text just describes current suffering without future danger (use Sympathy Appeal).", "Text attacks person's character (use Emotional Manipulation).", "Explicit threat/sanction from persuader (use Threat)."]
        }
    },
    {
        "name": "Emotional Manipulation",
        "description": "persuader strategically shifts moods, exaggerates emotions, or exploits the other person's feelings to push them toward donating.",
        "parent_category": "Emotional Influence",
        "parent_id": "emotional",
        "subclass_id": "sympathy",
        "subclass_name": "Emotional Manipulation",
        "markers": ["you don't care", "heartless", "cruel", "selfish", "if you had a heart", "how can you not", "you're being", "manipulative pressure", "no compassion", "cold-hearted"],
        "decision_rules": {
            "use_if": ["Text manipulates emotions with coercion, attacks person's character, or uses emotional blackmail to force donation."],
            "avoid_if": ["Mainly facts, duty, exchange, or authority.", "Text just describes suffering without attacking (use Sympathy Appeal).", "Text asks to imagine situation (use Empathy Appeal).", "Text uses shame/guilt about actions, not character attack (use Guilt Induction)."]
        }
    },
    
    # Urgency / Scarcity (30-32)
    {
        "name": "Urgency",
        "description": "persuader stresses that time is running out and that the donation must happen immediately.",
        "parent_category": "Urgency / Scarcity",
        "parent_id": "urgency_scarcity",
        "subclass_id": "urgency_time",
        "subclass_name": "Urgency (Time Pressure)",
        "markers": ["urgent", "right now", "today", "hours left", "until midnight", "immediately"],
        "decision_rules": {
            "use_if": ["Text emphasizes deadlines, limited time, limited slots, match windows."],
            "avoid_if": ["No limitation cues; only general request.", "Limitation is not time but quantity (use scarcity_quantity)"]
        }
    },
    {
        "name": "Scarcity",
        "description": "persuader stresses that time, resources, or opportunities are limited, so the person should donate now before it is too late.",
        "parent_category": "Urgency / Scarcity",
        "parent_id": "urgency_scarcity",
        "subclass_id": "scarcity_quantity",
        "subclass_name": "Scarcity (Limited Quantity/Opportunity)",
        "markers": ["limited spots", "only 5 left", "last 10", "few remaining", "running out", "almost gone", "nearly full", "only a few", "almost complete", "running low"],
        "decision_rules": {
            "use_if": ["Text emphasizes specific limited quantity/opportunity with concrete numbers or clear indication of scarcity."],
            "avoid_if": ["No limitation cues; only general request.", "Primary cue is deadline/time (use Urgency).", "Text uses artificial urgency phrases like 'hurry up' or 'act now' without concrete scarcity (use Scarcity Manipulation)."]
        }
    },
    # Threat / Pressure (31-35)
    {
        "name": "Threat",
        "description": "persuader explicitly warns that negative consequences will follow if the other person does not donate.",
        "parent_category": "Threat / Pressure",
        "parent_id": "threat_pressure",
        "subclass_id": "threat_sanction",
        "subclass_name": "Threat (Sanction by Persuader)",
        "markers": ["otherwise I'll block", "I'll complain", "there will be consequences", "last warning"],
        "decision_rules": {
            "use_if": ["Text explicitly warns that negative consequences will follow if person does not donate ('otherwise I'll block', 'I'll complain', 'there will be consequences', 'last warning')."],
            "avoid_if": ["Only external fear about victims without sanction by persuader (use Emotional parent).", "Fear about external events rather than sanction (use Fear Appeal).", "Persistent pressure without explicit threat (use Aversive Stimulation)."]
        }
    },
    {
        "name": "Aversive Stimulation",
        "description": "persuader creates or maintains discomfort, tension, or unpleasant pressure until the other person agrees to donate.",
        "parent_category": "Threat / Pressure",
        "parent_id": "threat_pressure",
        "subclass_id": "aversive_pressure",
        "subclass_name": "Aversive Pressure (Persistent Discomfort)",
        "markers": ["what's up", "when will you transfer", "I'm waiting", "don't ignore", "answer now"],
        "decision_rules": {
            "use_if": ["Text creates or maintains discomfort, tension, or unpleasant pressure without explicit threat ('what's up', 'when will you transfer', 'I'm waiting', 'don't ignore', 'answer now')."],
            "avoid_if": ["Only external fear about victims without sanction by persuader.", "Contains explicit threat/sanction (use Threat)."]
        }
    },
    {
        "name": "Punishing Activity",
        "description": "persuader warns that something bad or unpleasant will happen if the other person refuses to donate.",
        "parent_category": "Threat / Pressure",
        "parent_id": "threat_pressure",
        "subclass_id": "threat_sanction",
        "subclass_name": "Threat (Sanction by Persuader) - Punishment variant",
        "markers": ["otherwise", "bad", "unpleasant", "otherwise I'll block"],
        "decision_rules": {
            "use_if": ["Text warns that something bad or unpleasant will happen if person refuses ('otherwise', 'bad', 'unpleasant', 'otherwise I'll block')."],
            "avoid_if": ["Only external fear about victims without sanction by persuader.", "Explicit detailed threat/sanction (use Threat)."]
        }
    },
    {
        "name": "Overloading",
        "description": "persuader presents a large amount of information, details, or options in a way that overwhelms the other person and nudges them to donate.",
        "parent_category": "Threat / Pressure",
        "parent_id": "threat_pressure",
        "subclass_id": "aversive_pressure",
        "subclass_name": "Aversive Pressure (Persistent Discomfort) - Overloading variant",
        "markers": ["many", "all", "details", "options"],
        "decision_rules": {
            "use_if": ["Text presents large amount of information, details, or options in overwhelming way ('many', 'all', 'details', 'options', information overload)."],
            "avoid_if": ["Only external fear about victims without sanction by persuader.", "Makes things unclear/complicated without overwhelming (use Confusion Induction)."]
        }
    },
    {
        "name": "Confusion Induction",
        "description": "persuader makes things complicated, unclear, or contradictory so that the other person is disoriented and more likely to comply and donate.",
        "parent_category": "Threat / Pressure",
        "parent_id": "threat_pressure",
        "subclass_id": "aversive_pressure",
        "subclass_name": "Aversive Pressure (Persistent Discomfort) - Confusion variant",
        "markers": ["unclear", "complicated", "contradiction"],
        "decision_rules": {
            "use_if": ["Text makes things complicated, unclear, or contradictory to disorient person ('unclear', 'complicated', 'contradiction', confusing language)."],
            "avoid_if": ["Only external fear about victims without sanction by persuader.", "Presents overwhelming amount of info without confusion (use Overloading)."]
        }
    },
    
    # Call to Action (37-38)
    {
        "name": "Call to Action",
        "description": "persuader directly instructs or urges the other person to donate now, using clear action-oriented language.",
        "parent_category": "Call to Action",
        "parent_id": "call_to_action",
        "subclass_id": "cta_direct",
        "subclass_name": "Direct CTA",
        "markers": ["donate", "transfer", "here's the link", "here are the details"],
        "decision_rules": {
            "use_if": ["Text directly instructs or urges person to donate now with clear action language and link/requisites ('donate', 'transfer', 'here's the link', 'here are the details')."],
            "avoid_if": ["If another lever dominates (morality, exchange, fear, authority), treat CTA as secondary metadata.", "Strong urgency/scarcity present (use Urgency/Scarcity parent).", "Builds friendliness/similarity without direct imperative (use Liking)."]
        }
    },
    {
        "name": "Liking",
        "description": "persuader builds friendliness, similarity, or personal warmth to make the other person more willing to donate.",
        "parent_category": "Call to Action",
        "parent_id": "call_to_action",
        "subclass_id": "cta_direct",
        "subclass_name": "Direct CTA - Liking variant",
        "markers": ["friend", "brother", "as a friend"],
        "decision_rules": {
            "use_if": ["Text builds friendliness, similarity, or personal warmth to make person more willing to donate ('friend', 'brother', 'as a friend', 'we're alike')."],
            "avoid_if": ["If another lever dominates (morality, exchange, fear, authority), treat as secondary metadata.", "Direct imperative with link/requisites (use Call to Action)."]
        }
    },
    
    # Framing & Presentation (39-42)
    {
        "name": "Framing",
        "description": "persuader presents the same situation or outcome in a particular way to make donating look more attractive or reasonable.",
        "parent_category": "Framing & Presentation",
        "parent_id": "framing_presentation",
        "subclass_id": "framing",
        "subclass_name": "Framing",
        "markers": ["how", "instead", "better", "simpler"],
        "decision_rules": {
            "use_if": ["Text presents the same situation or outcome in a particular way to make donating look more attractive or reasonable ('how', 'instead', 'better', 'simpler', framing language)."],
            "avoid_if": ["Other levers dominate.", "Focus is on loss/missed opportunity (use Loss Aversion Appeal).", "Changes conditions/request mid-conversation (use Bait-and-switch).", "Creates false scenario/role (use Pretexting)."]
        }
    },
    {
        "name": "Loss Aversion Appeal",
        "description": "persuader emphasizes what will be lost or missed if the other person does not donate.",
        "parent_category": "Framing & Presentation",
        "parent_id": "framing_presentation",
        "subclass_id": "loss_aversion",
        "subclass_name": "Loss Aversion Appeal",
        "markers": ["you'll lose", "you'll miss", "won't get"],
        "decision_rules": {
            "use_if": ["Text emphasizes what will be lost or missed if person does not donate ('you'll lose', 'you'll miss', 'won't get', 'missed opportunity')."],
            "avoid_if": ["Other levers dominate.", "Focus is on general framing without loss emphasis (use Framing).", "Changes offer mid-conversation (use Bait-and-switch)."]
        }
    },
    {
        "name": "Bait-and-switch",
        "description": "persuader attracts the other person with one offer or description and then changes the conditions or the request to obtaining a donation.",
        "parent_category": "Framing & Presentation",
        "parent_id": "framing_presentation",
        "subclass_id": "bait_switch",
        "subclass_name": "Bait-and-switch",
        "markers": ["first", "then", "turns out"],
        "decision_rules": {
            "use_if": ["Text attracts person with one offer or description then changes conditions/request to obtaining donation ('first', 'then', 'turns out', changing conditions)."],
            "avoid_if": ["Other levers dominate.", "No change of conditions, just framing (use Framing)."]
        }
    },
    {
        "name": "Pretexting",
        "description": "persuader creates or maintains a false scenario, role, or story in order to justify asking for a donation.",
        "parent_category": "Framing & Presentation",
        "parent_id": "framing_presentation",
        "subclass_id": "pretexting",
        "subclass_name": "Pretexting",
        "markers": ["I'm calling from", "we are contacting", "I represent", "we're reaching out", "on behalf of", "supposedly", "claims to be", "pretends to be", "calling as", "contacting you as"],
        "decision_rules": {
            "use_if": ["Text creates or maintains a false scenario, role, or story to justify donation request ('I'm calling from', 'we are contacting', 'I represent', 'on behalf of', false identity)."],
            "avoid_if": ["Other levers dominate.", "No false identity, just framing (use Framing)."]
        }
    },
    
    # Conversation Management (43-51)
    {
        "name": "Greeting / Rapport",
        "description": "Non-persuasive greeting, opening, or rapport-building message that does not directly attempt to influence a donation decision.",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "greeting",
        "subclass_name": "Greeting / Rapport",
        "markers": ["hello", "hi", "hey", "how are you"],
        "decision_rules": {
            "use_if": ["Message is a greeting or rapport-building without donation pressure or request."],
            "avoid_if": ["Message includes donation instruction/link/amount request (use Call to Action).", "Message includes urgency/deadline pressure (use Urgency)."]
        }
    },
    {
        "name": "Permission / Time Check",
        "description": "Non-persuasive permission-seeking or time-check message to keep the conversation going (pre-suasion).",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "permission",
        "subclass_name": "Permission / Time Check",
        "markers": ["do you have a moment", "do you have time", "can we talk", "are you free"],
        "decision_rules": {
            "use_if": ["Message asks for time/permission to continue and does not contain donation pressure or request."],
            "avoid_if": ["Message includes donation instruction/link/amount request (use Call to Action).", "Message includes urgency/deadline pressure (use Urgency)."]
        }
    },
    {
        "name": "Charity Awareness Probe",
        "description": "Non-persuasive awareness/recognition probe about a charity/organization (lead-in question).",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "awareness_probe",
        "subclass_name": "Awareness Probe (Charity Familiarity)",
        "markers": ["have you heard of", "are you familiar with", "do you know about", "have you ever heard", "do you know this charity"],
        "decision_rules": {
            "use_if": ["Message asks whether the person knows/has heard of an organization/cause, without pressure or request."],
            "avoid_if": ["Message contains a direct donation request, link, or payment instructions (use Call to Action)."]
        }
    },
    {
        "name": "Qualification / Segmentation",
        "description": "Non-persuasive screening questions to segment the listener (e.g., parent status, demographics, eligibility).",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "qualification",
        "subclass_name": "Qualification / Segmentation",
        "markers": ["are you a parent", "do you have children", "how old are you", "where are you from", "are you a student", "do you work"],
        "decision_rules": {
            "use_if": ["Message is a screening/segmentation question and does not pressure donation."],
            "avoid_if": ["Message uses shame/guilt or coercion (use guilt_shame or threat_pressure)."]
        }
    },
    {
        "name": "Donation Baseline / Habit Probe",
        "description": "Non-persuasive question about donation habits, typical giving amount, or past giving behavior (baseline).",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "donation_baseline",
        "subclass_name": "Donation Baseline Probe",
        "markers": ["how much do you typically give", "how much do you donate", "do you donate", "in a year"],
        "decision_rules": {
            "use_if": ["Message asks about past/typical donation behavior or amounts without direct pressure."],
            "avoid_if": ["Message requests a donation NOW or provides link/requisites (use Call to Action).", "Message uses social pressure ('everyone donates') (use Social Proof)."]
        }
    },
    {
        "name": "Logistics / Coordination",
        "description": "Non-persuasive coordination message about donation process, logistics, or technical details without direct pressure.",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "logistics",
        "subclass_name": "Logistics / Coordination",
        "markers": ["how to donate", "donation process", "payment method", "transfer details", "donation details"],
        "decision_rules": {
            "use_if": ["Message provides technical/logistical information without strong pressure or urgency."],
            "avoid_if": ["Message contains urgent deadline or scarcity (use Urgency/Scarcity).", "Message contains strong emotional pressure or moral appeal."]
        }
    },
    {
        "name": "Acknowledgement",
        "description": "Non-persuasive acknowledgement, agreement, or neutral response to the other person's message.",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "acknowledgement",
        "subclass_name": "Acknowledgement",
        "markers": ["ok", "yes", "I see", "I understand", "got it", "okay"],
        "decision_rules": {
            "use_if": ["Message is a neutral acknowledgement or agreement without donation pressure."],
            "avoid_if": ["Message includes donation request or pressure (use appropriate persuasion strategy)."]
        }
    },
    {
        "name": "Conversation Closing",
        "description": "Non-persuasive closing, polite goodbye, thanking for the chat, ending the conversation.",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "closing",
        "subclass_name": "Closing / Goodbye",
        "markers": ["thanks for", "nice conversation", "have a nice day", "take care", "goodbye"],
        "decision_rules": {
            "use_if": ["Message ends the conversation politely without donation pressure."],
            "avoid_if": ["Message contains a last-minute donation push (use Urgency or Call to Action)."]
        }
    },
    {
        "name": "Non-persuasive Other",
        "description": "Other non-persuasive conversational messages that do not fit into specific categories above and do not directly attempt to influence a donation decision.",
        "parent_category": "Conversation Management",
        "parent_id": "conversation_management",
        "subclass_id": "other",
        "subclass_name": "Non-persuasive Other",
        "markers": [],
        "decision_rules": {
            "use_if": ["Message is conversational but does not contain persuasion tactics or donation pressure."],
            "avoid_if": ["Message contains any persuasion strategy (use appropriate category)."]
        }
    },
]

# Category structure for two-step hierarchical classification
STRATEGY_CATEGORIES = {
    "exchange": {
        "name": "Exchange / Incentives",
        "definition": "Donation request framed as an exchange: reward, gift, return favor, or owed obligation.",
        "parent_markers": ["in exchange", "for donation", "you'll get", "discount", "gift", "I to you", "you to me", "owe"],
        "strategies": ["Rewarding Activity", "Pre-giving", "Reciprocity", "Debt"]
    },
    "authority_expertise": {
        "name": "Authority / Expertise",
        "definition": "Uses perceived credibility: expertise, official status, or transparency proofs.",
        "parent_markers": ["officially", "foundation", "representative", "experience", "expert", "report", "receipts", "can verify"],
        "strategies": ["Expertise", "Authority", "Credibility Appeal"]
    },
    "norms_morality": {
        "name": "Norms / Morality / Values",
        "definition": "Appeals to moral correctness, values, duty, or guilt/shame.",
        "parent_markers": ["right", "conscience", "ashamed", "must", "should", "humanely", "morally"],
        "strategies": ["Moral Appeal", "Appeal to Values", "Activation of Impersonal Commitment", "Guilt Induction", "Self-feeling Appeal"]
    },
    "commitment": {
        "name": "Commitment / Consistency",
        "definition": "Uses past promises, intentions, or self-image consistency to push donation.",
        "parent_markers": ["you said", "you promised", "we agreed", "be consistent", "you always"],
        "strategies": ["Activation of Personal Commitment", "Commitment and Consistency", "Foot-in-the-door", "Door-in-the-face"]
    },
    "social_influence": {
        "name": "Social Influence",
        "definition": "Uses group behavior, belonging, or social comparison.",
        "parent_markers": ["everyone", "many", "already", "ours", "community", "normal people"],
        "strategies": ["Social Proof", "Unity", "Social Positioning"]
    },
    "rational": {
        "name": "Rational / Impact Appeal",
        "definition": "Uses practical reasons, facts, efficiency, structured arguments.",
        "parent_markers": ["statistics", "numbers", "logical", "effect", "result", "report", "efficiency"],
        "strategies": ["Rational Appeal", "Logical Appeal"]
    },
    "emotional": {
        "name": "Emotional Influence",
        "definition": "Uses emotions: empathy, pity, stories, emotional pressure.",
        "parent_markers": ["pity", "suffering", "heart", "imagine", "crying", "story", "pain"],
        "strategies": ["Emotional Appeal", "Storytelling", "Empathy Appeal", "Sympathy Appeal", "Fear Appeal", "Emotional Manipulation"]
    },
    "urgency_scarcity": {
        "name": "Urgency / Scarcity",
        "definition": "Pressures donation by limited time or limited opportunity/slots/resources.",
        "parent_markers": ["urgent", "today", "until", "left", "last chance", "limit", "limited"],
        "strategies": ["Urgency", "Scarcity"]
    },
    "threat_pressure": {
        "name": "Threat / Pressure",
        "definition": "Uses explicit or implicit negative consequences or persistent discomfort to force donation.",
        "parent_markers": ["otherwise", "you'll regret", "I'll block", "I'll stop", "won't give up", "I'm waiting for answer", "last warning"],
        "strategies": ["Threat", "Aversive Stimulation", "Punishing Activity", "Overloading", "Confusion Induction"]
    },
    "call_to_action": {
        "name": "Call to Action",
        "definition": "Direct instruction to donate now with clear action language.",
        "parent_markers": ["transfer", "donate", "here's the link", "send", "support now", "click"],
        "strategies": ["Call to Action", "Liking"]
    },
    "framing_presentation": {
        "name": "Framing & Presentation",
        "definition": "Presents situation in particular way to make donating attractive.",
        "parent_markers": ["how", "instead", "better", "simpler", "you'll lose", "you'll miss"],
        "strategies": ["Framing", "Loss Aversion Appeal", "Bait-and-switch", "Pretexting"]
    },
    "conversation_management": {
        "name": "Conversation Management",
        "definition": "Non-persuasive conversational messages and pre-suasion funnel steps (greetings, screening, awareness probes, coordination, acknowledgements) that do not directly attempt to influence a donation decision.",
        "parent_markers": ["hello", "hi", "?", "thanks", "ok", "have you heard", "are you familiar", "do you have a moment", "are you a parent"],
        "strategies": ["Greeting / Rapport", "Permission / Time Check", "Charity Awareness Probe", "Qualification / Segmentation", "Donation Baseline / Habit Probe", "Logistics / Coordination", "Acknowledgement", "Conversation Closing", "Non-persuasive Other"]
    }
}

